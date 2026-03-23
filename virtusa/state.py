from typing import TypedDict, Optional, List
from pydantic import BaseModel, Field

class TelemetryData(BaseModel):
    gaze: dict
    audio: dict
    keystrokes: dict
    code_snapshot: Optional[str] = None


class AnomalyDetectionOutput(BaseModel):
    """Structured output from Observer Agent"""
    anomalies: List[str] = Field(description="List of detected anomaly descriptions")
    anomaly_score: float = Field(ge=0.0, le=1.0, description="Anomaly score from 0.0 (clean) to 1.0 (definite cheating)")


class RiskAssessmentOutput(BaseModel):
    """Structured output from Logic Agent"""
    risk_level: str = Field(description="Risk level: 'low', 'medium', or 'high'")
    code_intent: str = Field(description="Description of what the code is doing")
    code_plagiarism_likelihood: float = Field(ge=0.0, le=1.0, description="Likelihood code is copied (0-1)")
    integrity_risk_summary: str = Field(description="Brief summary of integrity risk")


class AgentState(TypedDict):
    # Input
    raw_telemetry: dict

    # Observer Agent outputs
    detected_anomalies: List[str]
    anomaly_score: float

    # Logic Agent outputs
    risk_level: str          # "low" | "medium" | "high"
    risk_assessment: dict
    code_intent: Optional[str]

    # Decision Agent outputs
    decision: str            # "autonomous" | "escalate" | "log_only"
    intervention_action: Optional[str]

    # Logs
    decision_logs: List[dict]
    messages: List[str]