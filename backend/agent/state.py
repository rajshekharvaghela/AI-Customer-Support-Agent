"""LangGraph agent state definition."""

from typing import Annotated, TypedDict

import operator


class AgentState(TypedDict):
    """Shared state passed between LangGraph nodes."""

    customer_id: str
    order_id: str
    reason: str
    condition: str
    customer_data: dict
    order_data: dict
    policy_text: str
    refund_history: list
    messages: Annotated[list, operator.add]
    reasoning_steps: list[str]
    policy_rules_applied: list[str]
    decision: str
    final_message: str
    error: str
