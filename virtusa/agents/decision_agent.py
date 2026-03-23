# agents/decision_agent.py
import os
import sys
import json
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from state import AgentState

# Ensure logs directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
INTEGRITY_LOG_FILE = os.path.join(LOG_DIR, "integrity_logs.jsonl")


def persist_decision_log(log_entry: dict) -> None:
    """Persist decision log to JSONL file"""
    try:
        with open(INTEGRITY_LOG_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"⚠️  Failed to persist log: {e}")


def decision_agent(state: AgentState) -> AgentState:
    """
    The Supervisor. Reads shared state from Observer + Logic agents.
    Routes to Arrow A (autonomous) or Arrow B (escalate to human).
    Persists decision logs to JSONL file.
    """
    risk_level = state["risk_level"]
    anomaly_score = state["anomaly_score"]
    anomalies = state["detected_anomalies"]

    # Decision logic with thresholds
    if risk_level == "high" or anomaly_score > 0.75:
        decision = "escalate"           # Arrow B → Human Dashboard
        intervention_action = "FLAG_FOR_HUMAN_REVIEW"
    elif risk_level == "medium" or anomaly_score > 0.4:
        decision = "autonomous"         # Arrow A → Warning popup
        intervention_action = "SHOW_WARNING_POPUP"
    else:
        decision = "log_only"           # No intervention
        intervention_action = None

    # Build explainable log entry
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "intervention": intervention_action,
        "risk_level": risk_level,
        "anomaly_score": round(anomaly_score, 3),
        "anomalies": anomalies[:5],  # Limit to 5 for brevity
        "code_intent": state.get("code_intent", ""),
        "risk_assessment": state.get("risk_assessment", {}),
        "reasoning": f"Score={anomaly_score:.2f}, Risk={risk_level} → Decision: {decision}"
    }

    # Persist to JSONL
    persist_decision_log(log_entry)
    
    # Also add to decision_logs in state
    return {
        **state,
        "decision": decision,
        "intervention_action": intervention_action,
        "decision_logs": state["decision_logs"] + [log_entry],
        "messages": state["messages"] + [
            f"✓ Decision Agent: {decision.upper()} → {intervention_action or 'NO_ACTION'}"
        ]
    }