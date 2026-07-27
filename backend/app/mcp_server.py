import json
from typing import Dict, Any, List
from app.mcp_tools.map_tool import map_mcp
from app.mcp_tools.weather_tool import weather_mcp
from app.mcp_tools.camera_tool import camera_mcp
from app.mcp_tools.notification_tool import notification_mcp
from app.mcp_tools.hardware_tool import hardware_mcp

class GuardianMCPServer:
    """
    Model Context Protocol (MCP) Server for GuardianAI.
    Exposes emergency tools via standard MCP specification:
    - map_evaluate_evacuation_routes
    - weather_get_current_weather
    - camera_analyze_frame
    - notification_dispatch_alert
    - hardware_send_command
    """
    def __init__(self):
        self.server_info = {
            "name": "guardian-ai-mcp-server",
            "version": "1.0.0",
            "protocolVersion": "2024-11-05"
        }
        
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        MCP Specification: Returns tool definitions with descriptions and JSON schema input properties.
        """
        return [
            {
                "name": "map_evaluate_evacuation_routes",
                "description": "Evaluates building layout, primary exit doors (Gate A vs Gate B), blocked corridors, and nearest fire hydrants based on active hazard location.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "hazard_zone": {
                            "type": "string",
                            "description": "Room or corridor ID where fire or threat is located (e.g. 'Room 204')"
                        }
                    },
                    "required": ["hazard_zone"]
                }
            },
            {
                "name": "weather_get_current_weather",
                "description": "Retrieves local ambient weather parameters (wind speed, wind direction, humidity, temperature) to calculate disaster spread probability.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "lat": {"type": "number", "description": "GPS Latitude"},
                        "lon": {"type": "number", "description": "GPS Longitude"}
                    }
                }
            },
            {
                "name": "camera_analyze_frame",
                "description": "Performs optical inspection on surveillance image frame using Gemini Vision to verify flame luminosity, smoke plumes, or false alarm burnt toast.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "image_base64": {"type": "string", "description": "Base64 encoded JPEG image frame from ESP32-CAM"}
                    }
                }
            },
            {
                "name": "notification_dispatch_alert",
                "description": "Dispatches urgent emergency alerts across multi-channels: SIM800L Cellular SMS, Web Dashboard, and Email.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "recipients": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of emergency phone numbers or email addresses"
                        },
                        "message": {"type": "string", "description": "Emergency alert broadcast message text"},
                        "channels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Channels to use (e.g. ['SIM800L_SMS', 'DASHBOARD', 'EMAIL'])"
                        }
                    },
                    "required": ["recipients", "message"]
                }
            },
            {
                "name": "hardware_send_command",
                "description": "Commands physical ESP32 hardware actuators: turns Active Buzzer siren ON/OFF and sets Status LED to GREEN or RED.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "buzzer_on": {"type": "boolean", "description": "True to activate acoustic alarm buzzer siren, False to silence"},
                        "led_color": {"type": "string", "enum": ["GREEN", "RED"], "description": "Status LED color"},
                        "alarm_mode": {"type": "string", "description": "Alarm mode label (NORMAL / EMERGENCY)"}
                    },
                    "required": ["buzzer_on", "led_color"]
                }
            }
        ]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP Specification: Invokes target tool by name with arguments and returns structured response.
        """
        print(f"[MCP Server] Executing tool '{name}' with arguments: {arguments}")
        
        try:
            if name == "map_evaluate_evacuation_routes":
                zone = arguments.get("hazard_zone", "Room 204")
                res = map_mcp.evaluate_evacuation_routes(hazard_zone=zone)
                return {"status": "SUCCESS", "result": res}

            elif name == "weather_get_current_weather":
                lat = arguments.get("lat", 20.2961)
                lon = arguments.get("lon", 85.8245)
                res = weather_mcp.get_current_weather(lat=lat, lon=lon)
                return {"status": "SUCCESS", "result": res}

            elif name == "camera_analyze_frame":
                img = arguments.get("image_base64", "")
                res = camera_mcp.analyze_camera_frame(image_base64=img, sensor_context=arguments)
                return {"status": "SUCCESS", "result": res}

            elif name == "notification_dispatch_alert":
                recipients = arguments.get("recipients", [])
                msg = arguments.get("message", "EMERGENCY ALERT")
                ch = arguments.get("channels", ["SIM800L_SMS", "DASHBOARD", "EMAIL"])
                res = notification_mcp.dispatch_alert(recipients=recipients, message=msg, channels=ch)
                return {"status": "SUCCESS", "result": res}

            elif name == "hardware_send_command":
                buzzer = arguments.get("buzzer_on", False)
                led = arguments.get("led_color", "GREEN")
                mode = arguments.get("alarm_mode", "NORMAL")
                res = hardware_mcp.send_hardware_command(buzzer_on=buzzer, led_color=led, alarm_mode=mode)
                return {"status": "SUCCESS", "result": res}

            else:
                return {"status": "ERROR", "error": f"Tool '{name}' not recognized by MCP Server"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

# Singleton MCP Server Instance
mcp_server = GuardianMCPServer()
