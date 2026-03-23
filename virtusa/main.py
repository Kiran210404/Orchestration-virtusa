from dotenv import load_dotenv
load_dotenv()

import sys
import json
from datetime import datetime, timezone

if __name__ == "__main__":
    from graph import build_agentic_core

    print("\n" + "="*70)
    print("VIRTUSA - Interview Integrity Proctoring System")
    print("="*70)
    
    app = build_agentic_core()

    # Simulated input from Candidate Node
    initial_state = {
        "raw_telemetry": {
            "gaze": {"direction": "left", "duration_away_sec": 12},
            "audio": {"external_voice_detected": True, "confidence": 0.85},
            "keystrokes": {"paste_detected": True, "wpm": 240},
            "code_snapshot": "def two_sum(nums, target): return {v: i for i, v in enumerate(nums)}"
        },
        "detected_anomalies": [],
        "anomaly_score": 0.0,
        "risk_level": "",
        "risk_assessment": {},
        "code_intent": None,
        "decision": "",
        "intervention_action": None,
        "decision_logs": [],
        "messages": []
    }

    print("\n INPUT TELEMETRY:")
    print(f"  • Gaze: {initial_state['raw_telemetry']['gaze']}")
    print(f"  • Audio: {initial_state['raw_telemetry']['audio']}")
    print(f"  • Keystrokes: {initial_state['raw_telemetry']['keystrokes']}")
    print(f"  • Code: {initial_state['raw_telemetry']['code_snapshot'][:50]}...")
    
    print("\n  EXECUTING PIPELINE...")
    print("-" * 70)
    
    try:
        start_time = datetime.now(timezone.utc)
        result = app.invoke(initial_state)
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        print("\n PIPELINE EXECUTION SUCCESSFUL")
        print("="*70)
        
        print("\n EXECUTION TRACE:")
        for msg in result.get("messages", []):
            print(f"  → {msg}")
        
        print("\n BEHAVIORAL ANALYSIS:")
        print(f"  • Detected Anomalies: {len(result['detected_anomalies'])} found")
        for anomaly in result["detected_anomalies"][:3]:
            print(f"    - {anomaly}")
        print(f"  • Anomaly Score: {result['anomaly_score']:.2f}/1.0")
        
        print("\n  RISK ASSESSMENT:")
        print(f"  • Risk Level: {result['risk_level'].upper()}")
        print(f"  • Code Intent: {result['code_intent']}")
        print(f"  • Assessment: {json.dumps(result['risk_assessment'], indent=4)}")
        
        print("\n DECISION:")
        print(f"  • Decision: {result['decision'].upper()}")
        print(f"  • Intervention: {result['intervention_action'] or 'NONE'}")
        
        print("\n DECISION LOG ENTRY:")
        if result["decision_logs"]:
            log_entry = result["decision_logs"][-1]
            print(f"  • Timestamp: {log_entry['timestamp']}")
            print(f"  • Reasoning: {log_entry['reasoning']}")
        
        print("\n  PERFORMANCE:")
        print(f"  • Execution Time: {duration:.2f}s")
        print(f"  • Total Messages: {len(result['messages'])}")
        
        print("\n Logs saved to: logs/integrity_logs.jsonl")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n PIPELINE EXECUTION FAILED")
        print("="*70)
        print(f"Error: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Check .env file has valid OPENROUTER_API_KEY")
        print("  2. Ensure OpenRouter account has available credits")
        print("  3. Check internet connection")
        sys.exit(1)