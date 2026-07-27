from typing import Dict, Any, Optional
from app.mcp_client import mcp_client

class CommunicationAgent:
    """
    Agent 5: Communication Agent
    Dispatches emergency alerts via Notification MCP over MCP Client.
    Sends physical hardware actuation commands (Active Buzzer siren ON/OFF, Status LED RED/GREEN) over Hardware MCP over MCP Client.
    """
    def process(
        self, 
        verified_event: Dict[str, Any], 
        rescue_plan: Dict[str, Any],
        mqtt_client: Optional[Any] = None
    ) -> Dict[str, Any]:
        
        if not verified_event.get("verified"):
            # Send hardware command over MCP Client
            mcp_client.invoke_tool(
                tool_name="hardware_send_command",
                arguments={"buzzer_on": False, "led_color": "GREEN", "alarm_mode": "NORMAL"}
            )
            return {
                "agent_name": "Communication Agent",
                "status": "NOMINAL",
                "sim800l_action": "STANDBY",
                "hardware_actuation": {"buzzer": "OFF", "led": "GREEN"},
                "alerts_sent": []
            }

        recipients = ["occupants_floor2@building-a.org", "911_dispatch@city-emergency.gov", "+919876543210"]
        disaster_type = verified_event.get("disaster_type", "EMERGENCY")
        
        alert_msg = (
            f"🚨 EMERGENCY ALERT: CONFIRMED {disaster_type}!\n"
            f"Confidence: {verified_event.get('confidence', 90):.0f}%\n"
            f"EVACUATION ROUTE: {rescue_plan.get('recommended_exit', 'East Exit (Gate B)')}\n"
            f"GPS LOCATION: Lat {verified_event.get('gps_lat', 20.2961)}, Lon {verified_event.get('gps_lon', 85.8245)}\n"
            f"GUIDANCE: {rescue_plan.get('guidance', 'Evacuate immediately.')}"
        )

        # Dispatch via Notification MCP over MCP Client
        notif_mcp_resp = mcp_client.invoke_tool(
            tool_name="notification_dispatch_alert",
            arguments={"recipients": recipients, "message": alert_msg, "channels": ["SIM800L_SMS", "DASHBOARD", "EMAIL"]}
        )

        # Actuate Hardware via Hardware MCP over MCP Client
        hardware_mcp_resp = mcp_client.invoke_tool(
            tool_name="hardware_send_command",
            arguments={"buzzer_on": True, "led_color": "RED", "alarm_mode": "EMERGENCY"}
        )

        return {
            "agent_name": "Communication Agent",
            "status": "DISPATCHED",
            "mcp_sources": ["notification_dispatch_alert", "hardware_send_command"],
            "sim800l_action": "SMS_SENT_NETWORK_FOUND",
            "alert_message": alert_msg,
            "notification_result": notif_mcp_resp.get("result", {}),
            "hardware_actuation": hardware_mcp_resp.get("result", {})
        }

comms_agent = CommunicationAgent()
