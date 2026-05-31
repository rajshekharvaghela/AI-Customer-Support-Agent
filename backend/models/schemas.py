"""Pydantic schemas for refund agent API requests and responses."""

from pydantic import BaseModel, Field


class RefundRequest(BaseModel):
    """Structured refund request from the frontend."""

    customer_id: str
    order_id: str
    reason: str
    condition: str = Field(
        description='One of: "unopened", "opened", "damaged_shipping", "damaged_customer"'
    )


class AgentResponse(BaseModel):
    """Agent decision response returned to the client."""

    decision: str
    message: str
    reasoning_steps: list[str]
    policy_rules_applied: list[str]
    confidence: float = Field(ge=0.0, le=1.0)


class ConversationMessage(BaseModel):
    """Single message in a chat conversation."""

    role: str
    content: str
    timestamp: str


class ChatRequest(BaseModel):
    """Free-form chat request with optional conversation history."""

    customer_id: str
    message: str
    conversation_history: list[ConversationMessage] = []


class CustomerSummary(BaseModel):
    """Minimal customer info for dropdown lists."""

    customer_id: str
    name: str


class OrderSummary(BaseModel):
    """Order details returned to the frontend."""

    order_id: str
    product_name: str
    category: str
    amount: float
    order_date: str
    status: str
    is_final_sale: bool
    condition: str
