import json
from typing import Dict, Any, Optional

class HardwareMCPTool:
    """
    Hardware Command MCP Tool Adapter: Sends hardware actuation commands (Buzzer ON/OFF,
    LED status light GREEN/RED, display messaging) back to the physical or simulated ESP32 node.
    """
    def send_hardware_command(
        self, 
        buzzer_on: bool = False, 
        led_color: str = "GREEN", 
        alarm_mode: str = "NORMAL",
        mqtt_client: Optional[Any] = None
    ) -> Dict[str, Any]:
        
        command_payload = {
            "buzzer": "ON" if buzzer_on else "OFF",
            "led": led_color.upper(),
            "alarm_mode": alarm_mode,
            "display_msg": "EVACUATE IMMEDIATELY!" if buzzer_on else "SYSTEM NORMAL"
        }
        
        # Publish payload over MQTT if client connection is active
        if mqtt_client:
            try:
                mqtt_client.publish("guardian/hardware/command", json.dumps(command_payload))
                print(f"[HardwareMCP] Published MQTT command: {command_payload}")
            except Exception as e:
                print(f"[HardwareMCP] MQTT publish warning: {e}")
        else:
            print(f"[HardwareMCP] Simulated Hardware Actuation: {command_payload}")
            
        return {
            "status": "COMMAND_SENT",
            "payload": command_payload
        }

hardware_mcp = HardwareMCPTool()
