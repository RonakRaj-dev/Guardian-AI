import random
from typing import Dict, Any

class WeatherMCPTool:
    """
    Weather MCP Tool Adapter: Retrieves real-time local weather conditions
    (wind speed, direction, ambient temperature, humidity) to calculate disaster spread risk.
    """
    def get_current_weather(self, lat: float = 37.7749, lon: float = -122.4194) -> Dict[str, Any]:
        # Mock weather service with realistic parameters
        return {
            "temperature_celsius": 29.5,
            "humidity_percent": 22.0,  # Dry conditions
            "wind_speed_kmh": 18.5,
            "wind_direction": "SW",
            "wind_gusts_kmh": 28.0,
            "precipitation_mm": 0.0,
            "weather_condition": "Clear / Dry",
            "fire_risk_index": "HIGH"  # Dry & windy environment amplifies fire spread risk
        }

weather_mcp = WeatherMCPTool()
