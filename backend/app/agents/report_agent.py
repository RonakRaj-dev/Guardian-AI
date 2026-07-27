import time
from typing import Dict, Any, List
from datetime import datetime

class ReportAgent:
    """
    Agent 6: Report Agent
    Synthesizes an executive markdown incident report, complete with exact hardware sensor evidence,
    agent execution logs, false-alarm verification audit, and GPS location tracking.
    """
    def process(
        self, 
        telemetry: Dict[str, Any], 
        agent_logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        incident_id = f"INC-{int(time.time())}"

        verification_log = next((log for log in agent_logs if log.get("agent_name") == "Verification Agent"), {})
        rescue_log = next((log for log in agent_logs if log.get("agent_name") == "Rescue Planning Agent"), {})
        situation_log = next((log for log in agent_logs if log.get("agent_name") == "Situation Assessment Agent"), {})
        comms_log = next((log for log in agent_logs if log.get("agent_name") == "Communication Agent"), {})

        is_verified = verification_log.get("verified", False)
        is_false_alarm = verification_log.get("is_false_alarm", False)
        disaster_type = verification_log.get("disaster_type", "BUILDING_FIRE")

        gps_lat = telemetry.get("gps_lat", 20.2961)
        gps_lon = telemetry.get("gps_lon", 85.8245)

        report_md = f"""# GuardianAI Emergency Incident Report
**Incident ID**: {incident_id}  
**Timestamp**: {timestamp_str}  
**Status**: {"VERIFIED EMERGENCY" if is_verified else ("FALSE ALARM PREVENTED" if is_false_alarm else "NOMINAL MONITORING")}  
**Disaster Type**: {disaster_type}  
**GPS Coordinates**: Latitude: {gps_lat}, Longitude: {gps_lon} (NEO-6M Module)  
**GSM Status**: {telemetry.get('sim800l_status', 'NETWORK_FOUND')} (SIM800L Module)  

---

## 1. Multi-Agent System Audit Summary
| Agent Step | Status | Key Output / Decision |
|---|---|---|
"""
        for log in agent_logs:
            report_md += f"| **{log.get('agent_name')}** | {log.get('status', 'OK')} | {log.get('summary', log.get('rationale', log.get('guidance', 'Completed')))} |\n"

        report_md += f"""
---

## 2. Hardware Sensor Telemetry Evidence
- **DHT22 Temperature**: {telemetry.get('temperature', 32.5):.1f} °C
- **DHT22 Humidity**: {telemetry.get('humidity', 67.5):.1f} %
- **MQ2 Smoke/Gas Raw**: {telemetry.get('mq2_raw', 0)} / 4095
- **MQ135 Air Quality Raw**: {telemetry.get('mq135_raw', 0)} / 4095
- **Water Flood Level Raw**: {telemetry.get('water_raw', 0)} / 4095
- **MPU6050 3-Axis Accel**: AX = {telemetry.get('mpu_ax', 0.12):.2f}g, AY = {telemetry.get('mpu_ay', 0.05):.2f}g, AZ = {telemetry.get('mpu_az', 0.98):.2f}g (Total: {telemetry.get('vibration_g', 1.0):.2f} G)
- **Active Buzzer Actuator**: {comms_log.get('hardware_actuation', {}).get('payload', {}).get('buzzer', telemetry.get('buzzer_state', 'OFF'))}
- **Status LED Actuator**: {comms_log.get('hardware_actuation', {}).get('payload', {}).get('led', telemetry.get('led_state', 'GREEN'))}
- **SIM800L GSM SMS**: {comms_log.get('sim800l_action', 'STANDBY')}

---

## 3. Rescue & Evacuation Instructions
- **Recommended Exit**: {rescue_log.get('recommended_exit', 'N/A')}
- **Blocked Areas**: {', '.join(rescue_log.get('blocked_corridors', [])) or 'None'}
- **Responder ETA**: {rescue_log.get('responder_eta_mins', 'N/A')} minutes
- **Environmental Spread Risk**: {situation_log.get('spread_probability', 0):.1f}%

---
*Report generated automatically by GuardianAI Autonomous Agentic Engine.*
"""

        return {
            "agent_name": "Report Agent",
            "incident_id": incident_id,
            "timestamp": timestamp_str,
            "report_markdown": report_md,
            "status": "REPORT_GENERATED"
        }

report_agent = ReportAgent()
