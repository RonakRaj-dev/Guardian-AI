import time
import json
import sqlite3
import math
from typing import List, Dict, Any, Optional
from datetime import datetime

DB_PATH = "guardian_events.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop old telemetry table if schema lacks mq2_raw
    cursor.execute("PRAGMA table_info(telemetry)")
    telemetry_cols = [col[1] for col in cursor.fetchall()]
    if telemetry_cols and "mq2_raw" not in telemetry_cols:
        cursor.execute("DROP TABLE IF EXISTS telemetry")

    # Drop old incidents table if schema lacks gps_coords
    cursor.execute("PRAGMA table_info(incidents)")
    incidents_cols = [col[1] for col in cursor.fetchall()]
    if incidents_cols and "gps_coords" not in incidents_cols:
        cursor.execute("DROP TABLE IF EXISTS incidents")

    # Table for raw sensor telemetry matching exact hardware
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            timestamp REAL,
            temperature REAL,
            humidity REAL,
            mq2_raw INTEGER,
            mq135_raw INTEGER,
            water_raw INTEGER,
            mpu_ax REAL,
            mpu_ay REAL,
            mpu_az REAL,
            vibration_g REAL,
            gps_lat REAL,
            gps_lon REAL,
            sim800l_status TEXT,
            led_state TEXT,
            buzzer_state TEXT,
            flame_detected INTEGER,
            scream_detected INTEGER,
            image_base64 TEXT,
            status_raw TEXT
        )
    """)
    
    # Table for incidents and verified emergency events
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            timestamp REAL,
            status TEXT,
            disaster_type TEXT,
            confidence REAL,
            location TEXT,
            gps_coords TEXT,
            severity TEXT,
            evacuation_route TEXT,
            report_markdown TEXT,
            agents_log TEXT,
            created_at TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database schema
init_db()

class Repository:
    @staticmethod
    def save_telemetry(data: Dict[str, Any]):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        ax = float(data.get("mpu_ax", 0.12))
        ay = float(data.get("mpu_ay", 0.05))
        az = float(data.get("mpu_az", 0.98))
        vib_g = data.get("vibration_g")
        if vib_g is None:
            vib_g = math.sqrt(ax*ax + ay*ay + az*az)

        cursor.execute("""
            INSERT INTO telemetry 
            (device_id, timestamp, temperature, humidity, mq2_raw, mq135_raw, water_raw, mpu_ax, mpu_ay, mpu_az, vibration_g, gps_lat, gps_lon, sim800l_status, led_state, buzzer_state, flame_detected, scream_detected, image_base64, status_raw)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("device_id", "esp32-guardian-01"),
            data.get("timestamp", time.time()),
            float(data.get("temperature", 32.5)),
            float(data.get("humidity", 67.5)),
            int(data.get("mq2_raw", 120)),
            int(data.get("mq135_raw", 150)),
            int(data.get("water_raw", 10)),
            ax, ay, az, vib_g,
            float(data.get("gps_lat", 20.2961)),
            float(data.get("gps_lon", 85.8245)),
            data.get("sim800l_status", "NETWORK_FOUND"),
            data.get("led_state", "GREEN"),
            data.get("buzzer_state", "OFF"),
            1 if data.get("flame_detected") else 0,
            1 if data.get("scream_detected") else 0,
            data.get("image_base64", ""),
            json.dumps(data)
        ))
        conn.commit()
        conn.close()

    @staticmethod
    def get_latest_telemetry(limit: int = 50) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM telemetry ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for r in rows:
            results.append({
                "id": r[0],
                "device_id": r[1],
                "timestamp": r[2],
                "temperature": r[3],
                "humidity": r[4],
                "mq2_raw": r[5],
                "smoke_ppm": r[5] * 0.25 if r[5] else 0,
                "mq135_raw": r[6],
                "water_raw": r[7],
                "mpu_ax": r[8],
                "mpu_ay": r[9],
                "mpu_az": r[10],
                "vibration_g": r[11],
                "gps_lat": r[12],
                "gps_lon": r[13],
                "sim800l_status": r[14],
                "led_state": r[15],
                "buzzer_state": r[16],
                "flame_detected": bool(r[17]),
                "scream_detected": bool(r[18]),
                "image_base64": r[19],
                "formatted_time": datetime.fromtimestamp(r[2]).strftime("%H:%M:%S")
            })
        return results

    @staticmethod
    def save_incident(incident: Dict[str, Any]):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO incidents 
            (id, timestamp, status, disaster_type, confidence, location, gps_coords, severity, evacuation_route, report_markdown, agents_log, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            incident.get("id"),
            incident.get("timestamp", time.time()),
            incident.get("status", "ACTIVE"),
            incident.get("disaster_type", "FIRE"),
            incident.get("confidence", 0.0),
            incident.get("location", "Building A - 2nd Floor"),
            f"Lat: {incident.get('gps_lat', 20.2961)}, Lon: {incident.get('gps_lon', 85.8245)}",
            incident.get("severity", "MEDIUM"),
            incident.get("evacuation_route", ""),
            incident.get("report_markdown", ""),
            json.dumps(incident.get("agents_log", [])),
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()

    @staticmethod
    def get_incidents(limit: int = 10) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM incidents ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        incidents = []
        for r in rows:
            incidents.append({
                "id": r[0],
                "timestamp": r[1],
                "status": r[2],
                "disaster_type": r[3],
                "confidence": r[4],
                "location": r[5],
                "gps_coords": r[6],
                "severity": r[7],
                "evacuation_route": r[8],
                "report_markdown": r[9],
                "agents_log": json.loads(r[10]) if r[10] else [],
                "created_at": r[11]
            })
        return incidents
