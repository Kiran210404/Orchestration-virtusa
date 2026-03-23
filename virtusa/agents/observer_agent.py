# agents/observer_agent.py
import os
import sys
import json
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from state import AgentState, AnomalyDetectionOutput
from langchain_openai import ChatOpenAI

# Initialize LLM with reduced max_tokens to fit free tier limits
llm = ChatOpenAI(
    model="openai/gpt-oss-120b:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    max_tokens=300,  # Reduced from 1000 to fit free tier (4000 token limit)
    temperature=0.7,
)

# Use structured output
llm_structured = llm.with_structured_output(AnomalyDetectionOutput)

def log_to_file(message: str, log_file: str = "logs/observer_debug.log"):
    """Append message to debug log"""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {message}\n")


def observer_agent(state: AgentState) -> AgentState:
    """
    Receives raw telemetry (gaze, audio, keystrokes).
    Detects behavioral anomalies using structured LLM output.
    """
    telemetry = state["raw_telemetry"]
    
    try:
        prompt = f"""
Analyze the following real-time telemetry data for an interview proctoring system and detect anomalies.

Telemetry Data:
{json.dumps(telemetry, indent=2)}

Look for:
1. Unusual gaze patterns (looking away for extended periods, reading from external sources)
2. Audio anomalies (external voices detected, suspicious audio signals)
3. Keystroke patterns (copy-paste operations, unusually fast typing, suspicious pauses)

Provide your response in JSON format with:
- anomalies: list of detected anomaly descriptions (max 5)
- anomaly_score: float between 0.0 (clean) and 1.0 (definite cheating)
"""
        
        response = llm_structured.invoke(prompt)
        
        log_to_file(f"Observer Agent - Anomalies detected: {response.anomalies}, Score: {response.anomaly_score}")
        
        return {
            **state,
            "detected_anomalies": response.anomalies,
            "anomaly_score": response.anomaly_score,
            "messages": state["messages"] + ["Observer Agent: Behavioral analysis complete"]
        }
        
    except Exception as e:
        error_msg = f"Observer Agent Error: {str(e)}"
        log_to_file(error_msg)
        print(f"⚠️  {error_msg}")
        
        # Return state with empty anomalies on error
        return {
            **state,
            "detected_anomalies": ["ERROR: Could not analyze telemetry"],
            "anomaly_score": 0.5,  # Default to medium suspicion on error
            "messages": state["messages"] + [f"Observer Agent: {error_msg}"]
        }