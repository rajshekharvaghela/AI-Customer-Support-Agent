"""LangGraph StateGraph definition for the refund agent pipeline."""

from langgraph.graph import END, StateGraph

from backend.agent.nodes import (
    format_response_node,
    llm_reasoning_node,
    load_data_node,
    validate_request_node,
)
from backend.agent.state import AgentState


def should_call_llm(state: AgentState) -> str:
    """Conditional edge: only call LLM for PENDING cases."""
    if state["decision"] == "PENDING":
        return "llm_reasoning"
    return "format_response"


def build_agent_graph():
    """Build and compile the refund agent LangGraph pipeline."""
    graph = StateGraph(AgentState)

    graph.add_node("load_data", load_data_node)
    graph.add_node("validate_request", validate_request_node)
    graph.add_node("llm_reasoning", llm_reasoning_node)
    graph.add_node("format_response", format_response_node)

    graph.set_entry_point("load_data")
    graph.add_edge("load_data", "validate_request")
    graph.add_conditional_edges(
        "validate_request",
        should_call_llm,
        {
            "llm_reasoning": "llm_reasoning",
            "format_response": "format_response",
        },
    )
    graph.add_edge("llm_reasoning", "format_response")
    graph.add_edge("format_response", END)

    return graph.compile()


agent_graph = build_agent_graph()
