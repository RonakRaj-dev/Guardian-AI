from typing import Dict, Any
from app.mcp_client import mcp_client

class RescuePlanningAgent:
    """
    Agent 4: Rescue Planning Agent
    Queries Map MCP via MCP Client to compute optimal occupant evacuation pathways, 
    avoid hazardous corridors, determine responder access points, and locate nearest fire hydrants.
    """
    def process(self, situation_data: Dict[str, Any], hazard_location: str = "Room 204") -> Dict[str, Any]:
        if situation_data.get("severity") == "LOW":
            return {
                "agent_name": "Rescue Planning Agent",
                "status": "STANDBY",
                "recommended_exit": "N/A",
                "guidance": "Maintain standard safety monitoring."
            }

        # Invoke Map MCP Tool via MCP Client
        mcp_resp = mcp_client.invoke_tool(
            tool_name="map_evaluate_evacuation_routes",
            arguments={"hazard_zone": hazard_location}
        )

        map_data = mcp_resp.get("result", {})
        rec_exit = map_data.get("recommended_exit", {"name": "East Exit (Gate B)", "id": "Gate-B"})

        guidance = (
            f"PRIMARY EVACUATION INSTRUCTION: Proceed immediately to {rec_exit.get('name')}. "
            f"Avoid Main Corridor A (heavy smoke/hazard core). "
            f"Nearest Fire Hydrant located at {map_data.get('nearest_hydrant', {}).get('location', 'Outside Gate B Entrance')}. "
            f"Dispatched {map_data.get('nearest_fire_station', {}).get('name', 'Central Fire Station #4')} "
            f"(ETA: {map_data.get('nearest_fire_station', {}).get('eta_minutes', 4.5)} mins)."
        )

        return {
            "agent_name": "Rescue Planning Agent",
            "status": "PLAN_GENERATED",
            "mcp_source": "map_evaluate_evacuation_routes",
            "recommended_exit": rec_exit.get("name"),
            "exit_id": rec_exit.get("id"),
            "blocked_corridors": map_data.get("blocked_areas", []),
            "guidance": guidance,
            "responder_eta_mins": map_data.get("nearest_fire_station", {}).get("eta_minutes", 4.5),
            "map_details": map_data
        }

rescue_agent = RescuePlanningAgent()
