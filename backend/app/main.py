import os
import json
import asyncio
from typing import Dict, Any, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.config import settings
from app.database import Repository
from app.logger import guardian_logger
from app.mqtt_client import mqtt_manager
from app.mcp_client import mcp_client
from app.agents.crew_manager import guardian_crew_manager

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="GuardianAI Autonomous Disaster Response System - CrewAI + Groq LLM Engine"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        guardian_logger.info(f"[WebSocket] Client connected ({len(self.active_connections)} active)")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            guardian_logger.info(f"[WebSocket] Client disconnected ({len(self.active_connections)} active)")

    async def broadcast(self, message: Dict[str, Any]):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

ws_manager = ConnectionManager()

def process_incoming_telemetry(telemetry: Dict[str, Any]) -> Dict[str, Any]:
    # Save raw telemetry to database
    Repository.save_telemetry(telemetry)

    # Run CrewAI Multi-Agent Pipeline (Groq llama-3.3-70b-versatile)
    incident_result = guardian_crew_manager.run_crewai_disaster_pipeline(telemetry)

    payload = {
        "type": "TELEMETRY_UPDATE",
        "telemetry": telemetry,
        "incident": incident_result
    }
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(ws_manager.broadcast(payload))
    except Exception as e:
        guardian_logger.warning(f"WebSocket broadcast notice: {e}")

    return incident_result

@app.on_event("startup")
def startup_event():
    guardian_logger.info("=" * 60)
    guardian_logger.info(f"  Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    guardian_logger.info(f"  CrewAI Engine: Enabled | Groq Model: {settings.GROQ_MODEL}")
    guardian_logger.info("=" * 60)
    mqtt_manager.start(telemetry_callback=process_incoming_telemetry)

# Mount static files directory for OmniresQ Next.js dashboard
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    next_assets = os.path.join(static_dir, "_next")
    if os.path.exists(next_assets):
        app.mount("/_next", StaticFiles(directory=next_assets), name="_next")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "status": "ONLINE",
        "system": settings.PROJECT_NAME,
        "crewai_framework": "ENABLED",
        "groq_model": settings.GROQ_MODEL,
        "version": settings.VERSION,
        "documentation": "/docs"
    }

@app.get("/{full_path:path}")
async def serve_static_or_spa(full_path: str):
    if full_path.startswith("api/") or full_path.startswith("ws/"):
        raise HTTPException(status_code=404, detail="API route not found")
    
    target_path = os.path.join(static_dir, full_path)
    if os.path.isfile(target_path):
        return FileResponse(target_path)
    
    html_path = target_path + ".html"
    if os.path.isfile(html_path):
        return FileResponse(html_path)
        
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
        
    raise HTTPException(status_code=404, detail="Not Found")

# ==============================================================================
# Model Context Protocol (MCP) API Endpoints
# ==============================================================================
@app.get("/api/v1/mcp/tools")
def list_mcp_tools():
    return {
        "mcp_version": "2024-11-05",
        "tools": mcp_client.get_mcp_tools(),
        "llm_function_declarations": mcp_client.get_llm_function_declarations()
    }

@app.post("/api/v1/mcp/call")
def invoke_mcp_tool(payload: Dict[str, Any] = Body(...)):
    tool_name = payload.get("tool_name")
    arguments = payload.get("arguments", {})
    if not tool_name:
        raise HTTPException(status_code=400, detail="Missing 'tool_name' parameter")

    result = mcp_client.invoke_tool(tool_name, arguments)
    return result

@app.post("/api/v1/telemetry")
async def ingest_telemetry(data: Dict[str, Any] = Body(...)):
    incident = process_incoming_telemetry(data)
    return {
        "status": "PROCESSED",
        "incident": incident
    }

@app.get("/api/v1/telemetry/latest")
def get_latest_telemetry(limit: int = 20):
    return Repository.get_latest_telemetry(limit=limit)

@app.get("/api/v1/incidents")
def get_incidents(limit: int = 10):
    return Repository.get_incidents(limit=limit)

@app.post("/api/v1/hardware/command")
def send_manual_hardware_command(command: Dict[str, Any] = Body(...)):
    buzzer = command.get("buzzer", False)
    led = command.get("led", "GREEN")
    payload_str = json.dumps({"buzzer": "ON" if buzzer else "OFF", "led": led})
    mqtt_manager.publish(settings.MQTT_TOPIC_COMMAND, payload_str)
    return {"status": "COMMAND_DISPATCHED", "payload": payload_str}

@app.post("/api/v1/demo/trigger")
async def trigger_demo_scenario(payload: Dict[str, Any] = Body(...)):
    scenario = payload.get("scenario", "SAFE").upper()
    scenario_map = {
        "FIRE": "FIRE_EMERGENCY",
        "FLOOD": "FLOOD_EMERGENCY",
        "EARTHQUAKE": "FIRE_EMERGENCY", # Or seismic simulation
        "FALSE_ALARM": "FALSE_ALARM",
        "SAFE": "SAFE"
    }
    target_scenario = scenario_map.get(scenario, scenario)
    try:
        from hardware_simulator import create_telemetry_payload
        telemetry_data = create_telemetry_payload(target_scenario)
    except Exception:
        telemetry_data = {
            "device_id": "esp32-guardian-01",
            "timestamp": asyncio.get_event_loop().time(),
            "temperature": 68.5 if "FIRE" in target_scenario else 32.5,
            "humidity": 22.0 if "FIRE" in target_scenario else 67.5,
            "mq2_raw": 3450 if "FIRE" in target_scenario else (1850 if target_scenario == "FALSE_ALARM" else 180),
            "mq135_raw": 1950 if "FIRE" in target_scenario else 210,
            "water_raw": 3120 if "FLOOD" in target_scenario else 20,
            "mpu_ax": 0.12, "mpu_ay": 0.05, "mpu_az": 0.98, "vibration_g": 0.99,
            "gps_lat": 20.2961, "gps_lon": 85.8245,
            "sim800l_status": "NETWORK_FOUND",
            "led_state": "RED" if "EMERGENCY" in target_scenario else "GREEN",
            "buzzer_state": "ON" if "EMERGENCY" in target_scenario else "OFF",
            "flame_detected": "FIRE" in target_scenario,
            "scream_detected": "FIRE" in target_scenario
        }
    incident = process_incoming_telemetry(telemetry_data)
    return {
        "status": "PROCESSED",
        "scenario": scenario,
        "telemetry": telemetry_data,
        "incident": incident
    }


@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        latest = Repository.get_latest_telemetry(limit=1)
        incidents = Repository.get_incidents(limit=1)
        
        await websocket.send_json({
            "type": "INITIAL_STATE",
            "telemetry": latest[0] if latest else None,
            "incident": incidents[0] if incidents else None
        })

        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
