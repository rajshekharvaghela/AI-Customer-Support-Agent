"""Streamlit frontend for the Worknoon AI Refund Agent."""

from __future__ import annotations

import os
from datetime import datetime

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Worknoon AI Refund Agent",
    page_icon="🤖",
    layout="wide",
)

st.markdown(
    """
<style>
    .decision-approved { background-color: #d4edda; color: #155724; padding: 8px 16px;
        border-radius: 8px; font-weight: bold; display: inline-block; }
    .decision-denied { background-color: #f8d7da; color: #721c24; padding: 8px 16px;
        border-radius: 8px; font-weight: bold; display: inline-block; }
    .decision-escalated { background-color: #fff3cd; color: #856404; padding: 8px 16px;
        border-radius: 8px; font-weight: bold; display: inline-block; }
</style>
""",
    unsafe_allow_html=True,
)


def _init_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "logs" not in st.session_state:
        st.session_state.logs = []
    if "last_response" not in st.session_state:
        st.session_state.last_response = None


def _fetch_customers() -> list[dict]:
    """Fetch customer list from the backend API."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/customers", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return []


def _fetch_orders(customer_id: str) -> list[dict]:
    """Fetch orders for a customer from the backend API."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/customer/{customer_id}/orders", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return []


def _display_decision_badge(decision: str) -> None:
    """Render a colored decision badge."""
    icons = {"APPROVED": "🟢", "DENIED": "🔴", "ESCALATED": "🟡"}
    css_class = {
        "APPROVED": "decision-approved",
        "DENIED": "decision-denied",
        "ESCALATED": "decision-escalated",
    }
    icon = icons.get(decision, "⚪")
    css = css_class.get(decision, "decision-escalated")
    st.markdown(
        f'<span class="{css}">{icon} {decision}</span>',
        unsafe_allow_html=True,
    )


def _log_decision(response: dict, customer_id: str, order_id: str, amount: float = 0) -> None:
    """Append a decision to the admin logs."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "decision": response.get("decision"),
        "customer_id": customer_id,
        "order_id": order_id,
        "amount": amount,
        "reasoning_steps": response.get("reasoning_steps", []),
        "policy_rules_applied": response.get("policy_rules_applied", []),
        "message": response.get("message", ""),
        "confidence": response.get("confidence", 0),
    }
    st.session_state.logs.insert(0, log_entry)
    st.session_state.last_response = log_entry


_init_session_state()

tab_chat, tab_admin = st.tabs(["💬 Customer Chat", "📊 Admin Dashboard"])

with tab_chat:
    st.title("AI Refund Assistant")

    customers = _fetch_customers()
    if not customers:
        st.error(f"Cannot connect to backend at {BACKEND_URL}. Is the server running?")
        st.stop()

    customer_options = {f"{c['customer_id']} — {c['name']}": c["customer_id"] for c in customers}

    with st.sidebar:
        st.header("Customer Selection")
        selected_label = st.selectbox("Customer ID", options=list(customer_options.keys()))
        customer_id = customer_options[selected_label]

        orders = _fetch_orders(customer_id)
        if orders:
            st.subheader("Your Orders")
            for order in orders:
                st.caption(
                    f"**{order['order_id']}** — {order['product_name']} "
                    f"(${order['amount']:.2f}) [{order['status']}]"
                )

    col_form, col_chat = st.columns([1, 1])

    with col_form:
        st.subheader("Submit Refund Request")

        order_ids = [o["order_id"] for o in orders] if orders else []
        selected_order_id = st.selectbox("Select Order", options=order_ids) if order_ids else None

        reason = st.text_area("Reason for Refund", placeholder="Describe why you want a refund...")
        condition = st.radio(
            "Item Condition",
            options=["unopened", "opened", "damaged_shipping", "damaged_customer"],
            format_func=lambda x: {
                "unopened": "Unopened",
                "opened": "Opened",
                "damaged_shipping": "Damaged (Shipping)",
                "damaged_customer": "Damaged (My Fault)",
            }[x],
        )

        if st.button("Submit Refund Request", type="primary", use_container_width=True):
            if not selected_order_id or not reason.strip():
                st.warning("Please select an order and provide a reason.")
            else:
                try:
                    resp = requests.post(
                        f"{BACKEND_URL}/api/refund",
                        json={
                            "customer_id": customer_id,
                            "order_id": selected_order_id,
                            "reason": reason,
                            "condition": condition,
                        },
                        timeout=60,
                    )
                    resp.raise_for_status()
                    result = resp.json()
                    st.session_state.last_response = result

                    order_amount = next(
                        (o["amount"] for o in orders if o["order_id"] == selected_order_id),
                        0,
                    )
                    _log_decision(result, customer_id, selected_order_id, order_amount)

                    st.subheader("Decision")
                    _display_decision_badge(result["decision"])
                    st.write(result["message"])
                    st.caption(f"Confidence: {result['confidence']:.0%}")
                except requests.RequestException as exc:
                    st.error(f"Request failed: {exc}")

    with col_chat:
        st.subheader("Free-Form Chat")

        for msg in st.session_state.conversation_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if msg.get("decision"):
                    _display_decision_badge(msg["decision"])

        chat_input = st.chat_input("Ask about refunds, orders, or policies...")
        if chat_input:
            st.session_state.conversation_history.append(
                {"role": "user", "content": chat_input}
            )

            try:
                history_payload = [
                    {
                        "role": m["role"],
                        "content": m["content"],
                        "timestamp": datetime.now().isoformat(),
                    }
                    for m in st.session_state.conversation_history[:-1]
                ]
                resp = requests.post(
                    f"{BACKEND_URL}/api/chat",
                    json={
                        "customer_id": customer_id,
                        "message": chat_input,
                        "conversation_history": history_payload,
                    },
                    timeout=60,
                )
                resp.raise_for_status()
                result = resp.json()

                st.session_state.conversation_history.append(
                    {
                        "role": "assistant",
                        "content": result["message"],
                        "decision": result.get("decision"),
                    }
                )

                if result.get("reasoning_steps") and len(result["reasoning_steps"]) > 1:
                    order_match = selected_order_id or "CHAT"
                    _log_decision(result, customer_id, order_match)

                st.rerun()
            except requests.RequestException as exc:
                st.error(f"Chat failed: {exc}")

with tab_admin:
    st.title("Agent Reasoning Logs")

    col_clear, _ = st.columns([1, 4])
    with col_clear:
        if st.button("Clear Logs"):
            st.session_state.logs = []
            st.session_state.last_response = None
            st.rerun()

    if st.session_state.last_response:
        last = st.session_state.last_response
        st.subheader("Last Processed Request")
        st.markdown(f"**Decision:** {last.get('decision', 'N/A')} | **Time:** {last.get('timestamp', 'N/A')}")

        st.markdown("**Policy Rules Applied:**")
        for rule in last.get("policy_rules_applied", []):
            st.markdown(f"- `{rule}`")

        st.markdown("**Reasoning Timeline:**")
        for i, step in enumerate(last.get("reasoning_steps", []), 1):
            st.markdown(f"{i}. {step}")

        st.markdown("**Customer Message:**")
        st.info(last.get("message", ""))

    st.divider()
    st.subheader("Recent Decisions (Last 10)")

    if st.session_state.logs:
        recent = st.session_state.logs[:10]
        st.dataframe(
            [
                {
                    "Decision": log["decision"],
                    "Customer": log["customer_id"],
                    "Order": log["order_id"],
                    "Amount": f"${log.get('amount', 0):.2f}",
                    "Time": log["timestamp"][:19],
                }
                for log in recent
            ],
            use_container_width=True,
        )

        counts: dict[str, int] = {"APPROVED": 0, "DENIED": 0, "ESCALATED": 0}
        for log in st.session_state.logs:
            d = log.get("decision", "")
            if d in counts:
                counts[d] += 1

        st.subheader("Decision Distribution")
        st.bar_chart(counts)
    else:
        st.info("No decisions logged yet. Submit a refund request to see reasoning logs.")
