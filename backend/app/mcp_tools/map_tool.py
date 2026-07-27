from typing import Dict, Any, List

class MapMCPTool:
    """
    Map MCP Tool Adapter: Provides spatial floor plan queries, exit accessibility,
    hydrant positions, and emergency responder distance calculations.
    """
    def __init__(self):
        self.building_schematic = {
            "name": "Innovation Center - Building A",
            "floor": "2nd Floor",
            "exits": [
                {"id": "Gate-A", "name": "North Exit (Gate A)", "status": "AVAILABLE", "distance_m": 45, "capacity": "HIGH"},
                {"id": "Gate-B", "name": "East Exit (Gate B)", "status": "PRIMARY_SAFE", "distance_m": 25, "capacity": "HIGH"},
                {"id": "Stairwell-C", "name": "Emergency Stairwell C", "status": "AVAILABLE", "distance_m": 60, "capacity": "MEDIUM"}
            ],
            "corridors": [
                {"id": "Corridor-A", "name": "Main Hallway Corridor A", "status": "NORMAL"},
                {"id": "Corridor-B", "name": "East Wing Corridor B", "status": "CLEAR"}
            ],
            "hydrants": [
                {"id": "Hydrant-1", "location": "Outside Gate B Entrance", "status": "ACTIVE", "pressure_psi": 85},
                {"id": "Hydrant-2", "location": "North Parking Lot", "status": "ACTIVE", "pressure_psi": 90}
            ],
            "fire_stations": [
                {"name": "Central Fire Station #4", "distance_km": 2.4, "eta_minutes": 4.5},
                {"name": "Metro Emergency Unit #12", "distance_km": 4.1, "eta_minutes": 7.0}
            ]
        }

    def get_building_layout(self) -> Dict[str, Any]:
        return self.building_schematic

    def evaluate_evacuation_routes(self, hazard_zone: str = "Room 204") -> Dict[str, Any]:
        """
        Determines safest exit based on active hazard location.
        """
        exits = self.building_schematic["exits"]
        if hazard_zone in ["Room 204", "Corridor-A"]:
            # Corridor A is compromised by fire/smoke
            recommended = [e for e in exits if e["id"] == "Gate-B"][0]
            blocked = ["Corridor-A"]
            guidance = "Evacuate via East Wing (Gate B). Avoid Main Hallway Corridor A due to smoke accumulation."
        else:
            recommended = exits[0]
            blocked = []
            guidance = "Proceed to nearest illuminated emergency exit stairwell."
            
        return {
            "recommended_exit": recommended,
            "blocked_areas": blocked,
            "guidance": guidance,
            "nearest_hydrant": self.building_schematic["hydrants"][0],
            "nearest_fire_station": self.building_schematic["fire_stations"][0]
        }

map_mcp = MapMCPTool()
