import time
from typing import Dict, Any, List, Optional
from app.agents.detection_agent import detection_agent
from app.agents.verification_agent import verification_agent
from app.agents.situation_agent import situation_agent
from app.agents.rescue_agent import rescue_agent
from app.agents.comms_agent import comms_agent
from app.agents.report_agent import report_agent
from app.database import Repository

class GuardianWorkflowEngine:
    """
    Orchestrates the 6-agent workflow pipeline for GuardianAI.
    Executes agents sequentially, maintaining unified state and logging step-by-step reasoning.
    """
    def run_pipeline(self, telemetry: Dict[str, Any], mqtt_client: Optional[Any] = None) -> Dict[str, Any]:
        pipeline_start = time.time()
        agent_logs: List[Dict[str, Any]] = []

        # Step 1: Detection Agent
        det_out = detection_agent.process(telemetry)
        agent_logs.append(det_out)

        # Step 2: Verification Agent
        ver_out = verification_agent.process(telemetry, det_out)
        agent_logs.append(ver_out)

        # Step 3: Situation Assessment Agent
        sit_out = situation_agent.process(ver_out)
        agent_logs.append(sit_out)

        # Step 4: Rescue Planning Agent
        rec_out = rescue_agent.process(sit_out)
        agent_logs.append(rec_out)

        # Step 5: Communication Agent
        com_out = comms_agent.process(ver_out, rec_out, mqtt_client)
        agent_logs.append(com_out)

        # Step 6: Report Agent
        rep_out = report_agent.process(telemetry, agent_logs)
        agent_logs.append(rep_out)

        pipeline_duration_ms = (time.time() - pipeline_start) * 1000

        # Construct final incident object
        is_verified = ver_out.get("verified", False)
        is_false_alarm = ver_out.get("is_false_alarm", False)

        incident_record = {
            "id": rep_out["incident_id"],
            "timestamp": time.time(),
            "status": "VERIFIED_EMERGENCY" if is_verified else ("FALSE_ALARM" if is_false_alarm else "NOMINAL"),
            "disaster_type": "BUILDING_FIRE",
            "confidence": ver_out.get("confidence", 0.0),
            "location": "Innovation Center - Building A (2nd Floor)",
            "severity": sit_out.get("severity", "LOW"),
            "evacuation_route": rec_out.get("recommended_exit", "N/A"),
            "report_markdown": rep_out.get("report_markdown", ""),
            "agents_log": agent_logs,
            "pipeline_duration_ms": round(pipeline_duration_ms, 2)
        }

        # Save to database repository
        if is_verified or is_false_alarm:
            Repository.save_incident(incident_record)

        return incident_record

workflow_engine = GuardianWorkflowEngine()
