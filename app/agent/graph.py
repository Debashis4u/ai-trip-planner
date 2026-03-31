# app/agent/graph.py

from langgraph.graph import StateGraph, END
from app.agent.state import TripState
from app.agent.nodes.parse_node import parse_node
from app.agent.nodes.validate_node import validate_node
from app.agent.nodes.preferences_node import preferences_node
from app.agent.nodes.weather_node import weather_node
from app.agent.nodes.plan_node import plan_node
from app.agent.nodes.budget_check_node import budget_check_node
from app.agent.nodes.replan_node import replan_node
from app.agent.nodes.accommodation_node import accommodation_node
from app.agent.nodes.transportation_node import transportation_node
from app.agent.nodes.packing_list_node import packing_list_node
from app.agent.nodes.local_tips_node import local_tips_node

def should_replan(state: dict) -> str:
    """Decide whether to replan based on budget check"""
    if state.get("is_within_budget") is False:
        return "replan"
    return "accommodation"

def should_continue(state: dict) -> str:
    """Decide whether to continue based on validation"""
    if state.get("is_valid") is False:
        return END  # Stop processing if validation fails
    return "preferences"

def build_graph():
    builder = StateGraph(TripState)

    builder.add_node("parse", parse_node)
    builder.add_node("validate", validate_node)
    builder.add_node("preferences", preferences_node)
    builder.add_node("weather", weather_node)
    builder.add_node("plan", plan_node)
    builder.add_node("budget_check", budget_check_node)
    builder.add_node("replan", replan_node)
    builder.add_node("accommodation", accommodation_node)
    builder.add_node("transportation", transportation_node)
    builder.add_node("packing_list", packing_list_node)
    builder.add_node("local_tips", local_tips_node)

    builder.set_entry_point("parse")

    builder.add_edge("parse", "validate")
    
    # Conditional routing based on validation
    builder.add_conditional_edges(
        "validate",
        should_continue,
        {
            "preferences": "preferences",
            END: END
        }
    )
    
    builder.add_edge("preferences", "weather")
    builder.add_edge("weather", "plan")
    builder.add_edge("plan", "budget_check")
    
    # Conditional routing based on budget check
    builder.add_conditional_edges(
        "budget_check",
        should_replan,
        {
            "replan": "replan",
            "accommodation": "accommodation"
        }
    )
    
    # Loop back from replan to budget_check
    builder.add_edge("replan", "budget_check")
    
    # After budget is approved, add accommodation and transportation
    builder.add_edge("accommodation", "transportation")
    builder.add_edge("transportation", "packing_list")
    builder.add_edge("packing_list", "local_tips")
    builder.add_edge("local_tips", END)

    return builder.compile()