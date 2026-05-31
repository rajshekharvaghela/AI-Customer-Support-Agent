"""LangChain tool definitions for the refund agent."""

from __future__ import annotations

import json
from datetime import datetime

from langchain_core.tools import tool

from backend.database import db_service

REFERENCE_DATE = datetime(2026, 5, 31)


def _days_since_order(order_date: str) -> int:
    """Calculate days elapsed since the order date."""
    order_dt = datetime.strptime(order_date, "%Y-%m-%d")
    return (REFERENCE_DATE - order_dt).days


@tool
def query_customer_order(customer_id: str, order_id: str) -> str:
    """
    Retrieves full details of a customer's order from the CRM database.
    Returns order details including product, amount, date, status, and sale type.
    """
    customer = db_service.get_customer_by_id(customer_id)
    if customer is None:
        return json.dumps({"error": f"Customer {customer_id} not found"})

    order = db_service.get_order_by_id(customer_id, order_id)
    if order is None:
        return json.dumps({"error": f"Order {order_id} not found for customer {customer_id}"})

    return json.dumps(
        {
            "customer_id": customer_id,
            "customer_name": customer["name"],
            "order": order,
        },
        indent=2,
    )


@tool
def check_refund_eligibility(
    order_date: str,
    category: str,
    amount: float,
    is_final_sale: bool,
    condition: str,
    is_clearance: bool,
    refund_history_count: int,
) -> str:
    """
    Checks if an order is eligible for refund based on corporate policy rules.
    Returns a structured eligibility result with reasons.
    """
    days_elapsed = _days_since_order(order_date)
    window = 14 if category == "electronics" else 30
    rules_applied: list[str] = []
    blockers: list[str] = []
    decision = "ELIGIBLE"

    if is_final_sale:
        blockers.append("Final sale items are never eligible for refund (Rule 3.1)")
        rules_applied.append("Rule 3.1 — Final Sale")

    if is_clearance or category == "clearance":
        blockers.append("Clearance items are not eligible for refund (Rule 3.2)")
        rules_applied.append("Rule 3.2 — Clearance")

    if days_elapsed > window:
        blockers.append(
            f"Order is {days_elapsed} days old, exceeding the {window}-day window (Rule 2.1/2.2)"
        )
        rules_applied.append(f"Rule 2.{'2' if category == 'electronics' else '1'} — Return Window")

    if condition == "opened":
        blockers.append("Item must be in unopened condition (Rule 4.1)")
        rules_applied.append("Rule 4.1 — Unopened Condition")

    if condition == "damaged_customer":
        blockers.append("Customer-caused damage is not eligible (Rule 4.2)")
        rules_applied.append("Rule 4.2 — Customer Damage")

    if refund_history_count > 2:
        blockers.append(
            f"Customer has {refund_history_count} refunds in 60 days — escalate (Rule 6.1)"
        )
        rules_applied.append("Rule 6.1 — Refund Abuse")
        decision = "ESCALATE"

    if amount > 500:
        blockers.append(f"Amount ${amount:.2f} exceeds $500 — human escalation required (Rule 5.3)")
        rules_applied.append("Rule 5.3 — High-Value Escalation")
        decision = "ESCALATE"

    if blockers and decision != "ESCALATE":
        decision = "INELIGIBLE"
    elif not blockers:
        if amount < 100:
            rules_applied.append("Rule 5.1 — Auto-Approve Under $100")
            decision = "AUTO_APPROVE"
        elif amount <= 500:
            rules_applied.append("Rule 5.2 — Validated Approval $100–$500")
            decision = "APPROVE"

    if condition == "damaged_shipping" and decision in ("ELIGIBLE", "AUTO_APPROVE", "APPROVE"):
        rules_applied.append("Rule 4.3 — Shipping Damage Approved")

    return json.dumps(
        {
            "decision": decision,
            "days_elapsed": days_elapsed,
            "return_window_days": window,
            "blockers": blockers,
            "rules_applied": rules_applied,
        },
        indent=2,
    )


@tool
def get_policy_document() -> str:
    """
    Retrieves the full corporate refund policy document.
    Use this to verify specific policy rules before making decisions.
    """
    from backend.policy.policy_service import get_refund_policy

    return get_refund_policy()
