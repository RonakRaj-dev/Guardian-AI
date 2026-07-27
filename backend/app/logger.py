import os
import sys
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

LOG_FILE = "guardian_system.log"

# Configure logging format
log_format = logging.Formatter(
    fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Root logger setup
logger = logging.getLogger("GuardianAI")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)

# File handler
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

class GuardianLogger:
    @staticmethod
    def info(msg: str):
        logger.info(msg)

    @staticmethod
    def warning(msg: str):
        logger.warning(msg)

    @staticmethod
    def error(msg: str, exc: Optional[Exception] = None):
        if exc:
            err_details = f"{msg} | Exception: {str(exc)}\n{traceback.format_exc()}"
            logger.error(err_details)
        else:
            logger.error(msg)

    @staticmethod
    def log_telemetry_ingest(device_id: str, data: Dict[str, Any]):
        logger.info(
            f"📥 TELEMETRY INGEST [{device_id}] | Temp: {data.get('temperature')}°C | "
            f"MQ2: {data.get('mq2_raw')} | MQ135: {data.get('mq135_raw')} | "
            f"Water: {data.get('water_raw')} | Accel: {data.get('vibration_g')}G | "
            f"GPS: ({data.get('gps_lat')}, {data.get('gps_lon')})"
        )

    @staticmethod
    def log_agent_start(agent_name: str, role: str):
        logger.info(f"🤖 AGENT START -> [{agent_name}] (Role: {role})")

    @staticmethod
    def log_agent_success(agent_name: str, status: str, summary: str, duration_ms: float = 0.0):
        logger.info(f"✅ AGENT SUCCESS -> [{agent_name}] Status: {status} | Latency: {duration_ms:.2f}ms | Output: {summary}")

    @staticmethod
    def log_agent_error(agent_name: str, error_msg: str, exc: Optional[Exception] = None):
        logger.error(f"❌ AGENT FAILURE -> [{agent_name}] {error_msg}")
        if exc:
            logger.error(traceback.format_exc())

    @staticmethod
    def log_disaster_prediction(disaster_type: str, confidence: float, verified: bool, is_false_alarm: bool):
        if verified:
            logger.info(f"🚨 DISASTER PREDICTION VERIFIED -> Type: {disaster_type} | Confidence: {confidence:.1f}%")
        elif is_false_alarm:
            logger.info(f"⚠️ FALSE ALARM SUPPRESSED -> Type: {disaster_type} | Confidence: {confidence:.1f}%")
        else:
            logger.info(f"ℹ️ NOMINAL DISASTER PREDICTION -> Status: Safe")

    @staticmethod
    def log_mcp_tool_call(tool_name: str, arguments: Dict[str, Any], status: str, result: Any):
        logger.info(f"🛠️ MCP TOOL EXECUTION -> Tool: [{tool_name}] | Status: {status} | Args: {arguments}")

guardian_logger = GuardianLogger()
