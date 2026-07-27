from typing import Dict, Any
from app.mcp_client import mcp_client

class SituationAssessmentAgent:
    """
    Agent 3: Situation Assessment Agent
    Queries Weather MCP via MCP Client for wind direction & humidity,
    and projects disaster spread probability and structural threat level.
    """
    def process(self, verified_event: Dict[str, Any]) -> Dict[str, Any]:
        if not verified_event.get("verified"):
            return {
                "agent_name": "Situation Assessment Agent",
                "severity": "LOW",
                "spread_probability": 0.0,
                "assessment": "No active emergency verified."
            }

        # Invoke Weather MCP Tool via MCP Client
        mcp_resp = mcp_client.invoke_tool(
            tool_name="weather_get_current_weather",
            arguments={"lat": 20.2961, "lon": 85.8245}
        )

        weather = mcp_resp.get("result", {})
        wind_speed = weather.get("wind_speed_kmh", 18.5)
        humidity = weather.get("humidity_percent", 22.0)

        # Calculate fire/disaster spread probability
        spread_prob = 60.0 + (wind_speed * 1.2) - (humidity * 0.4)
        spread_prob = max(10.0, min(95.0, spread_prob))

        severity = "CRITICAL" if spread_prob > 75.0 else ("HIGH" if spread_prob > 50.0 else "MEDIUM")

        assessment = (
            f"Severity rated {severity}. External weather conditions from Weather MCP (Wind: {wind_speed} km/h {weather.get('wind_direction')}, "
            f"Humidity: {humidity}%) indicate a spread probability of {spread_prob:.1f}%."
        )

        return {
            "agent_name": "Situation Assessment Agent",
            "status": "ASSESSMENT_COMPLETE",
            "mcp_source": "weather_get_current_weather",
            "severity": severity,
            "spread_probability": spread_prob,
            "weather_data": weather,
            "assessment": assessment
        }

situation_agent = SituationAssessmentAgent()
