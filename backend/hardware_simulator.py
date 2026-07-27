import time
import json
import math
import random
import requests
from typing import Dict, Any

BACKEND_URL = "http://127.0.0.1:8000/api/v1/telemetry"

SAMPLE_CAM_IMAGE = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)

def create_telemetry_payload(scenario: str) -> Dict[str, Any]:
    timestamp = time.time()
    
    if scenario == "SAFE":
        return {
            "device_id": "esp32-guardian-01",
            "timestamp": timestamp,
            "temperature": 32.5,
            "humidity": 67.5,
            "mq2_raw": 180,              # Nominal Smoke 0-4095
            "mq135_raw": 210,            # Nominal Air Quality 0-4095
            "water_raw": 20,             # No water 0-4095
            "mpu_ax": 0.12,
            "mpu_ay": 0.05,
            "mpu_az": 0.98,
            "vibration_g": 0.99,
            "gps_lat": 20.2961,
            "gps_lon": 85.8245,
            "sim800l_status": "NETWORK_FOUND",
            "led_state": "GREEN",
            "buzzer_state": "OFF",
            "flame_detected": False,
            "scream_detected": False,
            "image_base64": SAMPLE_CAM_IMAGE
        }
        
    elif scenario == "FALSE_ALARM":
        return {
            "device_id": "esp32-guardian-01",
            "timestamp": timestamp,
            "temperature": 32.5,          # Normal ambient temp!
            "humidity": 67.5,
            "mq2_raw": 1850,             # High Smoke MQ2 ADC!
            "mq135_raw": 320,
            "water_raw": 15,
            "mpu_ax": 0.12,
            "mpu_ay": 0.05,
            "mpu_az": 0.98,
            "vibration_g": 0.99,
            "gps_lat": 20.2961,
            "gps_lon": 85.8245,
            "sim800l_status": "NETWORK_FOUND",
            "led_state": "GREEN",
            "buzzer_state": "OFF",
            "flame_detected": False,      # No optical flame!
            "scream_detected": False,
            "image_base64": SAMPLE_CAM_IMAGE
        }
        
    elif scenario == "FIRE_EMERGENCY":
        return {
            "device_id": "esp32-guardian-01",
            "timestamp": timestamp,
            "temperature": 68.5,          # High Temp!
            "humidity": 22.0,
            "mq2_raw": 3450,             # Severe Smoke MQ2 ADC!
            "mq135_raw": 1950,           # High Toxic Air MQ135!
            "water_raw": 10,
            "mpu_ax": 0.35,
            "mpu_ay": 0.28,
            "mpu_az": 1.25,
            "vibration_g": 1.33,
            "gps_lat": 20.2961,
            "gps_lon": 85.8245,
            "sim800l_status": "SMS_SENT_NETWORK_FOUND",
            "led_state": "RED",
            "buzzer_state": "ON",
            "flame_detected": True,       # Optical flame ACTIVE!
            "scream_detected": True,
            "image_base64": SAMPLE_CAM_IMAGE
        }
        
    elif scenario == "FLOOD_EMERGENCY":
        return {
            "device_id": "esp32-guardian-01",
            "timestamp": timestamp,
            "temperature": 31.0,
            "humidity": 92.0,
            "mq2_raw": 150,
            "mq135_raw": 180,
            "water_raw": 3120,            # High Water Level ADC 3120/4095!
            "mpu_ax": 0.10,
            "mpu_ay": 0.04,
            "mpu_az": 0.99,
            "vibration_g": 0.99,
            "gps_lat": 20.2961,
            "gps_lon": 85.8245,
            "sim800l_status": "SMS_SENT_NETWORK_FOUND",
            "led_state": "RED",
            "buzzer_state": "ON",
            "flame_detected": False,
            "scream_detected": False,
            "image_base64": SAMPLE_CAM_IMAGE
        }
    return {}

def send_payload(payload: Dict[str, Any]):
    print(f"\n[HARDWARE SIMULATOR] Sending Hardware Telemetry Node {payload.get('device_id')}...")
    print(f"  DHT22 Temp    : {payload.get('temperature')} °C | Humidity: {payload.get('humidity')} %")
    print(f"  MQ2 Smoke ADC : {payload.get('mq2_raw')} / 4095")
    print(f"  MQ135 Air ADC : {payload.get('mq135_raw')} / 4095")
    print(f"  Water Level   : {payload.get('water_raw')} / 4095")
    print(f"  MPU6050 3-Axis: AX={payload.get('mpu_ax')}g AY={payload.get('mpu_ay')}g AZ={payload.get('mpu_az')}g")
    print(f"  GPS NEO-6M    : Lat {payload.get('gps_lat')}, Lon {payload.get('gps_lon')}")
    print(f"  SIM800L GSM   : {payload.get('sim800l_status')}")
    
    try:
        resp = requests.post(BACKEND_URL, json=payload, timeout=5)
        if resp.status_code == 200:
            result = resp.json()
            incident = result.get("incident", {})
            print(f"  STATUS        : {incident.get('status')}")
            print(f"  CONFIDENCE    : {incident.get('confidence')}%")
            print(f"  EVAC ROUTE    : {incident.get('evacuation_route')}")
        else:
            print(f"  HTTP Error    : {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"  Connection Error: Make sure backend server is running on {BACKEND_URL}! ({e})")

def main():
    print("=" * 60)
    print("  GUARDIAN AI - HARDWARE SENSOR NODE SIMULATOR")
    print("=" * 60)
    print("Select a scenario to trigger hardware telemetry update:")
    print("  1) Send Normal Safe Hardware Telemetry (32.5°C, MQ2 180)")
    print("  2) Send False Alarm Scenario (MQ2 Smoke 1850 ADC, Temp 32.5°C)")
    print("  3) Send Active Building Fire Emergency (MQ2 3450 ADC, Temp 68.5°C)")
    print("  4) Send Flood / Water Level Emergency (Water 3120 ADC)")
    print("  5) Auto-pulse telemetry stream every 3 seconds")
    print("  Q) Quit")
    print("-" * 60)

    while True:
        choice = input("\nEnter option (1-5, Q): ").strip().upper()
        if choice == "1":
            send_payload(create_telemetry_payload("SAFE"))
        elif choice == "2":
            send_payload(create_telemetry_payload("FALSE_ALARM"))
        elif choice == "3":
            send_payload(create_telemetry_payload("FIRE_EMERGENCY"))
        elif choice == "4":
            send_payload(create_telemetry_payload("FLOOD_EMERGENCY"))
        elif choice == "5":
            print("[SIMULATOR] Pulsing safe hardware telemetry... Press Ctrl+C to stop.")
            try:
                while True:
                    send_payload(create_telemetry_payload("SAFE"))
                    time.sleep(3)
            except KeyboardInterrupt:
                print("\n[SIMULATOR] Stopped auto-pulse.")
        elif choice == "Q":
            print("Exiting simulator.")
            break

if __name__ == "__main__":
    main()
