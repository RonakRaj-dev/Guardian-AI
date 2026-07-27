# GuardianAI Hardware Setup & Multi-Sensor Wiring Diagram

This directory contains the production C++/Arduino firmware sketch (`esp32_guardian_node.ino`) for the ESP32 Guardian Node.

## Hardware Components List
1. **ESP32 Microcontroller** (ESP32-DevModule / ESP32-S3)
2. **DHT22 Sensor**: Temperature (32.5 °C) & Humidity (67.5 %) -> Digital GPIO 4
3. **MQ2 Smoke Sensor**: Smoke / Combustible Gas ADC (0 - 4095) -> Analog GPIO 34
4. **MQ135 Air Quality Sensor**: Air Quality / Toxic Gas ADC (0 - 4095) -> Analog GPIO 36 (VP)
5. **Water Level Sensor**: Flood Detection ADC (0 - 4095) -> Analog GPIO 33
6. **MPU6050 Accelerometer**: 3-Axis Seismic Acceleration (AX=0.12g, AY=0.05g, AZ=0.98g) -> I2C SDA (21) / SCL (22)
7. **GPS NEO-6M Module**: Live Location Tracking (Lat: 20.2961, Lon: 85.8245) -> Hardware Serial2 (RX 16 / TX 17)
8. **SIM800L GSM Module**: Cellular SMS Alert Dispatch & Network Status -> Serial1 (RX 26 / TX 27)
9. **Status Indicator LEDs**: Green LED (GPIO 14) / Red LED (GPIO 12)
10. **Active Piezo Alarm Buzzer**: Emergency Siren (GPIO 13)

---

## ESP32 Pinout Mapping Table

| Hardware Module | Module Pin | ESP32 GPIO Pin | Description |
|---|---|---|---|
| **DHT22** | Data | **GPIO 4** | Temp (°C) & Humidity (%) |
| **MQ2 Smoke** | A0 (Analog) | **GPIO 34** | Smoke ADC (0 - 4095) |
| **MQ135 Air** | A0 (Analog) | **GPIO 36 (VP)** | Toxic Air ADC (0 - 4095) |
| **Water Level** | Signal | **GPIO 33** | Flood Inundation (0 - 4095) |
| **MPU6050** | SDA / SCL | **GPIO 21 (SDA) / 22 (SCL)** | 3-Axis Accel (AX, AY, AZ) |
| **GPS NEO-6M** | TX / RX | **GPIO 16 (RX) / 17 (TX)** | Lat/Lon Location |
| **SIM800L GSM**| TX / RX | **GPIO 26 (RX) / 27 (TX)** | SMS Dispatch & GSM Signal |
| **Status LED Green**| Anode (+) | **GPIO 14** | System Nominal Indicator |
| **Status LED Red**| Anode (+) | **GPIO 12** | System Danger Indicator |
| **Active Buzzer**| Positive (+) | **GPIO 13** | Emergency Acoustic Siren |

---

## Telemetry JSON Payload Format
The ESP32 publishes telemetry to MQTT topic `guardian/sensor/telemetry` formatted as:
```json
{
  "device_id": "esp32-guardian-01",
  "timestamp": 1784917450,
  "temperature": 32.5,
  "humidity": 67.5,
  "mq2_raw": 180,
  "mq135_raw": 210,
  "water_raw": 20,
  "mpu_ax": 0.12,
  "mpu_ay": 0.05,
  "mpu_az": 0.98,
  "gps_lat": 20.2961,
  "gps_lon": 85.8245,
  "sim800l_status": "NETWORK_FOUND"
}
```
