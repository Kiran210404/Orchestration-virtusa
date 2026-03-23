# graph.py
from langgraph.graph import StateGraph, END
from state import AgentState
from agents.observer_agent import observer_agent
from agents.logic_agent import logic_agent
from agents.decision_agent import decision_agent

def build_agentic_core():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("observer", observer_agent)
    graph.add_node("logic", logic_agent)
    graph.add_node("decision", decision_agent)

    # Define flow: Observer → Logic → Decision
    graph.set_entry_point("observer")
    graph.add_edge("observer", "logic")
    graph.add_edge("logic", "decision")

    # Conditional routing from Decision Agent
    def route_decision(state: AgentState):
        if state["decision"] == "escalate":
            return "escalate_to_human"  # Arrow B
        elif state["decision"] == "autonomous":
            return "autonomous_intervention"  # Arrow A
        else:
            return END

    graph.add_conditional_edges(
        "decision",
        route_decision,
        {
            "escalate_to_human": END,       # → Human Dashboard handler
            "autonomous_intervention": END,  # → Warning popup handler
            END: END
        }
    )

    return graph.compile()
