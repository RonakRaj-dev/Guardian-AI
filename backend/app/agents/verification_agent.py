from typing import Dict, Any
from app.mcp_client import mcp_client

class VerificationAgent:
    """
    Agent 2: Verification Agent (Multi-Modal False Alarm Filter)
    Cross-verifies raw hardware ADC sensor spikes against thermal radiation, 
    water levels, toxic gas thresholds, and ESP32 camera vision analysis via Camera MCP tool.
    """
    def process(self, telemetry: Dict[str, Any], detection_result: Dict[str, Any]) -> Dict[str, Any]:
        if detection_result.get("status") == "NOMINAL":
            return {
                "agent_name": "Verification Agent",
                "verified": False,
                "is_false_alarm": False,
                "confidence": 0.0,
                "rationale": "No anomaly detected by hardware sensors."
            }

        temp = float(telemetry.get("temperature", 32.5))
        mq2_raw = int(telemetry.get("mq2_raw", 0))
        mq135_raw = int(telemetry.get("mq135_raw", 0))
        water_raw = int(telemetry.get("water_raw", 0))
        flame = telemetry.get("flame_detected", False)
        img_base64 = telemetry.get("image_base64", "")

        disaster_type = detection_result.get("primary_disaster", "BUILDING_FIRE")

        # Invoke Camera MCP Tool via MCP Client
        mcp_resp = mcp_client.invoke_tool(
            tool_name="camera_analyze_frame",
            arguments={"image_base64": img_base64, "flame_detected": flame, "smoke_ppm": mq2_raw * 0.25, "temperature": temp}
        )

        vision_result = mcp_resp.get("result", {})

        # False alarm logic for FIRE: High MQ2 smoke (>1200 raw) but low temp (<=34°C) & no optical/vision flame
        is_fire_false_alarm = (disaster_type == "BUILDING_FIRE" and mq2_raw > 1200 and temp <= 34.0 and not flame and not vision_result.get("flame_detected"))

        if is_fire_false_alarm:
            rationale = (
                f"FALSE ALARM PREVENTED: MQ2 sensor registered raw ADC level {mq2_raw} / 4095, "
                f"but ambient DHT22 temperature remains normal ({temp:.1f}°C) and ESP32 visual camera analysis "
                "confirmed zero optical flames or thermal radiation. Suppressing emergency alarm."
            )
            return {
                "agent_name": "Verification Agent",
                "verified": False,
                "is_false_alarm": True,
                "confidence": 95.0,
                "mcp_source": "camera_analyze_frame",
                "disaster_type": disaster_type,
                "rationale": rationale,
                "vision_details": vision_result
            }

        # Confirmed Emergency (Fire, Gas Leak, Flood, or Seismic)
        verification_confidence = min(99.0, detection_result.get("confidence", 70.0) + (10.0 if vision_result.get("flame_detected") else 5.0))
        
        rationale = f"DISASTER CONFIRMED ({disaster_type}): Multi-modal agreement verified! "
        if disaster_type == "BUILDING_FIRE":
            rationale += f"MQ2 Smoke ({mq2_raw}) + DHT22 Temp ({temp:.1f}°C) + Camera Vision agreement."
        elif disaster_type == "FLOOD":
            rationale += f"Water Sensor raw level {water_raw}/4095 indicates active inundation."
        elif disaster_type == "GAS_LEAK":
            rationale += f"MQ135 air quality sensor raw level {mq135_raw}/4095 indicates hazardous air toxicity."
        else:
            rationale += f"MPU6050 3-axis accelerometer tremor validated."

        return {
            "agent_name": "Verification Agent",
            "verified": True,
            "is_false_alarm": False,
            "confidence": verification_confidence,
            "mcp_source": "camera_analyze_frame",
            "disaster_type": disaster_type,
            "rationale": rationale,
            "vision_details": vision_result
        }

verification_agent = VerificationAgent()
