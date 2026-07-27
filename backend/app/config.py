import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    PROJECT_NAME: str = "GuardianAI Autonomous Disaster Response System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # LLM & AI Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile")
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # MQTT Broker Settings
    MQTT_BROKER: str = os.getenv("MQTT_BROKER", "broker.hivemq.com")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", "1883"))
    MQTT_TOPIC_TELEMETRY: str = "guardian/sensor/telemetry"
    MQTT_TOPIC_COMMAND: str = "guardian/hardware/command"
    MQTT_TOPIC_ALERTS: str = "guardian/alerts/broadcast"
    
    # Threshold Defaults for Rules & Edge Heuristics
    SMOKE_THRESHOLD_PPM: float = 350.0
    TEMP_THRESHOLD_CELSIUS: float = 45.0
    VIBRATION_THRESHOLD_G: float = 2.5
    
    # Default Location Data
    BUILDING_NAME: str = "Innovation Center - Building A"
    BUILDING_FLOOR: str = "2nd Floor"
    GPS_LAT: float = 20.2961
    GPS_LON: float = 85.8245

settings = Settings()
