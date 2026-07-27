# GuardianAI - Autonomous Disaster Response System MVP

> **Hackathon MVP**: Combining **IoT hardware + Multi-Agent AI + Edge Vision + Cloud AI** for early disaster detection, false-alarm verification, dynamic rescue routing, and emergency notification.

---

## Architecture Overview

```
                 ESP32 Node / Hardware Simulator
            (MQ2, DHT22, MPU6050, ESP32-CAM, Buzzer)
                               │
                       MQTT / WebSockets
                               ▼
                        FastAPI Backend
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
   6-Agent Gemini Pipeline               MCP Tools Layer
   - Detection Agent                     - Map MCP
   - Verification Agent (False Alarm)    - Weather MCP
   - Situation Assessment Agent          - Camera MCP
   - Rescue Planning Agent               - Notification MCP
   - Communication Agent                 - Hardware MCP
   - Report Agent (Audit Log)
            │
            ▼
    React Command Dashboard
   - Interactive Floor Plan Schematic
   - Real-time Sensor Metrics Gauges
   - Live Agent Workflow Step-by-Step Execution
   - Interactive Hardware Simulator Panel
```

---

## 6 Specialized Agents
1. **Detection Agent**: Evaluates raw sensor data (smoke PPM, temp °C, vibration G).
2. **Verification Agent**: Prevents false alarms by cross-referencing smoke PPM with thermal jumps and ESP32 camera vision analysis.
3. **Situation Assessment Agent**: Queries weather MCP for wind speed & humidity to calculate disaster spread risk.
4. **Rescue Planning Agent**: Dynamically computes safest evacuation routes (Exit Gate B) and locates fire hydrants.
5. **Communication Agent**: Formulates emergency alerts (SMS/Email/Dashboard) and commands the ESP32 buzzer and red status LED.
6. **Report Agent**: Synthesizes an executive markdown incident report and audit log for emergency responders.

---

## Quick Start Guide

### 1. Launch the Backend & Dashboard
```bash
# Navigate to project directory
cd c:\Users\gamer\OneDrive\Desktop\Silicon_Hackathon_Project

# Start FastAPI application
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open **`http://127.0.0.1:8000`** in your browser to view the Command Dashboard!

---

### 2. Test Scenarios via Hardware Simulator
You can test the system with or without physical hardware plugged in!

#### Option A: Built-in Interactive Web Panel
Click the **"Hardware Simulator"** button at the top right of the Web Dashboard to select:
- **Preset 1**: Normal Safe Conditions
- **Preset 2**: Smoke Only (Burnt Toast - False Alarm Filter Demo!)
- **Preset 3**: Confirmed Building Fire Emergency

#### Option B: Standalone Python CLI Simulator
```bash
.venv\Scripts\python.exe backend\hardware_simulator.py
```

---

### 3. Physical ESP32 Hardware Integration
Flash `hardware/esp32_guardian_node.ino` onto an ESP32 using the Arduino IDE.
Refer to `hardware/README.md` for complete pinout diagrams and library details.
