# agents/logic_agent.py
import os
import sys
import json
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from state import AgentState, RiskAssessmentOutput
from langchain_openai import ChatOpenAI

# Initialize LLM with reduced max_tokens
llm = ChatOpenAI(
    model="openai/gpt-oss-120b:free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    max_tokens=400,  # Reduced from 1000
    temperature=0.7,
)

# Use structured output
llm_structured = llm.with_structured_output(RiskAssessmentOutput)

def log_to_file(message: str, log_file: str = "logs/logic_debug.log"):
    """Append message to debug log"""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {message}\n")


def logic_agent(state: AgentState) -> AgentState:
    """
    Receives anomalies + code snapshot.
    Performs deep risk assessment using structured LLM output.
    """
    anomalies = state["detected_anomalies"]
    anomaly_score = state["anomaly_score"]
    code_snapshot = state["raw_telemetry"].get("code_snapshot", "")
    
    try:
        prompt = f"""
You are a risk assessment engine for an interview integrity system.

Detected Anomalies: {json.dumps(anomalies)}
Anomaly Score: {anomaly_score:.2f}
Code Submitted: {code_snapshot}

Assess the following:
1. Is the code structure suspicious (possible plagiarism)?
2. Does code complexity match typing behavior?
3. What is the overall integrity risk level?

Provide your response in JSON format with:
- risk_level: "low", "medium", or "high"
- code_intent: what the code is intended to do
- code_plagiarism_likelihood: float 0.0-1.0
- integrity_risk_summary: brief summary of risks
"""
        
        response = llm_structured.invoke(prompt)
        
        log_to_file(f"Logic Agent - Risk: {response.risk_level}, Plagiarism: {response.code_plagiarism_likelihood}")
        
        return {
            **state,
            "risk_level": response.risk_level,
            "code_intent": response.code_intent,
            "risk_assessment": {
                "plagiarism_likelihood": response.code_plagiarism_likelihood,
                "integrity_summary": response.integrity_risk_summary,
                "anomaly_correlation": len(anomalies) > 0
            },
            "messages": state["messages"] + ["Logic Agent: Risk assessment complete"]
        }
        
    except Exception as e:
        error_msg = f"Logic Agent Error: {str(e)}"
        log_to_file(error_msg)
        print(f"⚠️  {error_msg}")
        
        # Default conservative response on error
        return {
            **state,
            "risk_level": "medium" if state["anomaly_score"] > 0.3 else "low",
            "code_intent": "Unable to assess",
            "risk_assessment": {
                "plagiarism_likelihood": 0.5,
                "integrity_summary": f"Error in analysis: {str(e)[:100]}",
                "anomaly_correlation": len(anomalies) > 0
            },
            "messages": state["messages"] + [f"Logic Agent: {error_msg}"]
        }