import math
from typing import Dict, Any

class DetectionAgent:
    """
    Agent 1: Detection Agent
    Continuously monitors raw telemetry streams from ESP32 hardware node:
    - DHT22 (Temp & Humidity)
    - MQ2 (Smoke/Gas ADC 0-4095)
    - MQ135 (Air Quality/Toxic Gas ADC 0-4095)
    - Water Sensor (Flood Level ADC 0-4095)
    - MPU6050 (3-Axis Accelerometer AX, AY, AZ)
    - GPS NEO-6M (Lat, Lon)
    - SIM800L GSM Network Status
    """
    def process(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        temp = float(telemetry.get("temperature", 32.5))
        humidity = float(telemetry.get("humidity", 67.5))
        mq2_raw = int(telemetry.get("mq2_raw", 0))
        mq135_raw = int(telemetry.get("mq135_raw", 0))
        water_raw = int(telemetry.get("water_raw", 0))
        
        ax = float(telemetry.get("mpu_ax", 0.12))
        ay = float(telemetry.get("mpu_ay", 0.05))
        az = float(telemetry.get("mpu_az", 0.98))
        vibration_g = math.sqrt(ax*ax + ay*ay + az*az)
        
        flame = telemetry.get("flame_detected", False)
        scream = telemetry.get("scream_detected", False)
        gps_lat = telemetry.get("gps_lat", 20.2961)
        gps_lon = telemetry.get("gps_lon", 85.8245)

        detected_hazards = []
        primary_disaster = "NOMINAL"
        confidence_accum = 0.0

        # Threat 1: Fire & Thermal Emergency (MQ2 > 1200 raw OR Temp > 45°C)
        if mq2_raw > 1200 or temp > 45.0 or flame:
            detected_hazards.append("ELEVATED_SMOKE_MQ2" if mq2_raw > 1200 else "THERMAL_SPIKE")
            if flame: detected_hazards.append("OPTICAL_FLAME")
            confidence_accum += 50.0
            primary_disaster = "BUILDING_FIRE"

        # Threat 2: Toxic Air / Gas Leak (MQ135 > 1500 raw)
        if mq135_raw > 1500:
            detected_hazards.append("TOXIC_GAS_MQ135")
            confidence_accum += 40.0
            if primary_disaster == "NOMINAL": primary_disaster = "GAS_LEAK"

        # Threat 3: Water Leak / Flood (Water Sensor > 1500 raw)
        if water_raw > 1500:
            detected_hazards.append("WATER_FLOOD_DETECTED")
            confidence_accum += 60.0
            if primary_disaster == "NOMINAL": primary_disaster = "FLOOD"

        # Threat 4: Structural Earthquake / Seismic Shake (vibration_g > 1.8g baseline ~1.0g)
        if vibration_g > 1.8:
            detected_hazards.append("SEISMIC_VIBRATION_MPU6050")
            confidence_accum += 45.0
            if primary_disaster == "NOMINAL": primary_disaster = "EARTHQUAKE"

        if scream:
            detected_hazards.append("ACOUSTIC_DISTRESS")
            confidence_accum += 20.0

        confidence = min(99.0, confidence_accum)
        anomaly_detected = len(detected_hazards) > 0

        summary = (
            f"Anomaly detected ({', '.join(detected_hazards)}) at GPS ({gps_lat}, {gps_lon}) with initial confidence {confidence:.1f}%."
            if anomaly_detected else "Telemetry nominal. Hardware sensors within safe parameters."
        )

        return {
            "agent_name": "Detection Agent",
            "status": "ANOMALY_DETECTED" if anomaly_detected else "NOMINAL",
            "primary_disaster": primary_disaster,
            "hazards": detected_hazards,
            "confidence": confidence,
            "summary": summary,
            "gps_location": {"lat": gps_lat, "lon": gps_lon}
        }

detection_agent = DetectionAgent()
