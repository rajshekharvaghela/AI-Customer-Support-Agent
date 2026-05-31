"""FastAPI application for the Worknoon AI Refund Agent."""

from __future__ import annotations

import os
import re
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agent.graph import agent_graph
from backend.database import db_service
from backend.llm_client import llm
from backend.models.schemas import (
    AgentResponse,
    ChatRequest,
    CustomerSummary,
    OrderSummary,
    RefundRequest,
)
from backend.policy import policy_service

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "minimax-m2.5:cloud")

app = FastAPI(
    title="Worknoon AI Refund Agent",
    description="Production-ready AI customer support refund processing API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _build_initial_state(request: RefundRequest) -> dict:
    """Create the initial LangGraph state from a refund request."""
    return {
        "customer_id": request.customer_id,
        "order_id": request.order_id,
        "reason": request.reason,
        "condition": request.condition,
        "customer_data": {},
        "order_data": {},
        "policy_text": "",
        "refund_history": [],
        "messages": [],
        "reasoning_steps": [],
        "policy_rules_applied": [],
        "decision": "PENDING",
        "final_message": "",
        "error": "",
    }


def _compute_confidence(decision: str, rules: list[str], error: str) -> float:
    """Estimate confidence based on decision type and rules applied."""
    if error:
        return 1.0
    if decision == "ESCALATED":
        return 0.75
    if decision == "PENDING":
        return 0.5
    rule_count = len(rules)
    if rule_count >= 3:
        return 0.95
    if rule_count >= 1:
        return 0.9
    return 0.85


def _state_to_response(result: dict) -> AgentResponse:
    """Convert LangGraph final state to an API response."""
    decision = result.get("decision", "DENIED")
    if decision == "PENDING":
        decision = "ESCALATED"
    return AgentResponse(
        decision=decision,
        message=result.get("final_message", "Unable to process your request."),
        reasoning_steps=result.get("reasoning_steps", []),
        policy_rules_applied=result.get("policy_rules_applied", []),
        confidence=_compute_confidence(decision, result.get("policy_rules_applied", []), result.get("error", "")),
    )


def _extract_order_id(message: str) -> str | None:
    """Extract an order ID pattern from free-form text."""
    match = re.search(r"ORD_\d{4,}", message, re.IGNORECASE)
    return match.group(0).upper() if match else None


def _is_refund_intent(message: str) -> bool:
    """Detect whether a chat message is a refund request."""
    keywords = (
        "refund",
        "return",
        "money back",
        "cancel order",
        "send back",
        "reimburse",
    )
    message_lower = message.lower()
    return any(kw in message_lower for kw in keywords)


def _infer_condition(message: str) -> str:
    """Infer item condition from chat message text."""
    message_lower = message.lower()
    if "shipping" in message_lower or "transit" in message_lower or "arrived damaged" in message_lower:
        return "damaged_shipping"
    if "damaged" in message_lower or "broken" in message_lower:
        return "damaged_customer"
    if "opened" in message_lower or "used" in message_lower:
        return "opened"
    return "unopened"


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "model": OLLAMA_MODEL}


@app.post("/api/refund", response_model=AgentResponse)
async def process_refund(request: RefundRequest) -> AgentResponse:
    """Process a structured refund request through the agent graph."""
    try:
        initial_state = _build_initial_state(request)
        result = agent_graph.invoke(initial_state)
        return _state_to_response(result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Refund processing failed: {exc}") from exc


@app.post("/api/chat", response_model=AgentResponse)
async def chat(request: ChatRequest) -> AgentResponse:
    """Handle free-form customer chat, routing refund requests to the agent."""
    try:
        order_id = _extract_order_id(request.message)

        if _is_refund_intent(request.message) and order_id:
            refund_req = RefundRequest(
                customer_id=request.customer_id,
                order_id=order_id,
                reason=request.message,
                condition=_infer_condition(request.message),
            )
            return await process_refund(refund_req)

        system_prompt = (
            "You are a helpful customer support assistant for Worknoon Inc. "
            "Help customers with general inquiries about orders, shipping, and returns. "
            "If they want a refund, ask them to provide their order ID (format: ORD_XXXX). "
            "Be friendly, concise, and professional.\n\n"
            f"Policy summary:\n{policy_service.get_policy_summary()}"
        )

        history_text = ""
        for msg in request.conversation_history[-6:]:
            history_text += f"{msg.role}: {msg.content}\n"

        user_content = f"{history_text}\nCustomer ({request.customer_id}): {request.message}"

        response = llm.invoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=user_content)]
        )
        content = response.content if hasattr(response, "content") else str(response)

        return AgentResponse(
            decision="APPROVED",
            message=content,
            reasoning_steps=["General support chat — no refund processing required"],
            policy_rules_applied=[],
            confidence=0.8,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {exc}") from exc


@app.get("/api/customers", response_model=list[CustomerSummary])
async def list_customers() -> list[CustomerSummary]:
    """Return all customers for the frontend dropdown."""
    try:
        customers = db_service.get_all_customers()
        return [
            CustomerSummary(customer_id=c["customer_id"], name=c["name"])
            for c in customers
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/customer/{customer_id}/orders", response_model=list[OrderSummary])
async def get_customer_orders(customer_id: str) -> list[OrderSummary]:
    """Return all orders for a specific customer."""
    try:
        customer = db_service.get_customer_by_id(customer_id)
        if customer is None:
            raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
        return [
            OrderSummary(
                order_id=o["order_id"],
                product_name=o["product_name"],
                category=o["category"],
                amount=o["amount"],
                order_date=o["order_date"],
                status=o["status"],
                is_final_sale=o["is_final_sale"],
                condition=o["condition"],
            )
            for o in customer.get("orders", [])
        ]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/policy")
async def get_policy() -> dict:
    """Return the full refund policy document."""
    try:
        return {"policy": policy_service.get_refund_policy()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
