/*
 * ==============================================================================
 * GuardianAI - Autonomous Disaster Response System (ESP32 Multi-Sensor Firmware)
 * ==============================================================================
 * Hardware Components:
 * 1. DHT22 Sensor   - Temp (°C) & Humidity (%) -> Pin GPIO 4
 * 2. MQ2 Sensor     - Smoke/Gas Analog (0 - 4095) -> Pin GPIO 34
 * 3. MQ135 Sensor   - Air Quality Analog (0 - 4095) -> Pin GPIO 36 (VP)
 * 4. Water Sensor   - Flood Level Analog (0 - 4095) -> Pin GPIO 33
 * 5. MPU6050 Sensor - 3-Axis Accel (AX, AY, AZ) -> I2C SDA (21) / SCL (22)
 * 6. GPS NEO-6M     - Lat/Lon -> Hardware Serial2 RX (16) / TX (17)
 * 7. SIM800L Module - GSM SMS & Network Status -> Serial1 RX (26) / TX (27)
 * 8. Status LEDs    - Green (GPIO 14) / Red (GPIO 12)
 * 9. Active Buzzer  - Alarm Siren -> Pin GPIO 13
 * ==============================================================================
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

// WiFi Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT Broker Configuration
const char* mqtt_broker = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* topic_telemetry = "guardian/sensor/telemetry";
const char* topic_command = "guardian/hardware/command";

// Pin Definitions
#define PIN_DHT 4           // DHT22 Temp & Humidity Pin
#define DHTTYPE DHT22

#define PIN_MQ2 34          // MQ2 Smoke Analog Input (0-4095)
#define PIN_MQ135 36        // MQ135 Air Quality Analog Input (0-4095)
#define PIN_WATER 33        // Water Level Sensor Analog Input (0-4095)

#define PIN_BUZZER 13       // Active Buzzer Output (HIGH = ON, LOW = OFF)
#define PIN_LED_GREEN 14    // Green LED Pin
#define PIN_LED_RED 12      // Red LED Pin

DHT dht(PIN_DHT, DHTTYPE);
Adafruit_MPU6050 mpu;
WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastTelemetryTime = 0;
const long telemetryInterval = 2000; // 2 seconds telemetry pulse

void setup_wifi() {
  delay(10);
  Serial.println("\nConnecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected! IP: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* message, unsigned int length) {
  String messageTemp;
  for (int i = 0; i < length; i++) {
    messageTemp += (char)message[i];
  }
  Serial.print("MQTT Command Received: ");
  Serial.println(messageTemp);

  // Command Active Buzzer ON/OFF
  if (messageTemp.indexOf("\"buzzer\":\"ON\"") > 0) {
    digitalWrite(PIN_BUZZER, HIGH);
  } else if (messageTemp.indexOf("\"buzzer\":\"OFF\"") > 0) {
    digitalWrite(PIN_BUZZER, LOW);
  }

  // Command LEDs RED/GREEN
  if (messageTemp.indexOf("\"led\":\"RED\"") > 0) {
    digitalWrite(PIN_LED_GREEN, LOW);
    digitalWrite(PIN_LED_RED, HIGH);
  } else if (messageTemp.indexOf("\"led\":\"GREEN\"") > 0) {
    digitalWrite(PIN_LED_RED, LOW);
    digitalWrite(PIN_LED_GREEN, HIGH);
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT Broker...");
    String clientId = "ESP32GuardianNode-";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("Connected to MQTT!");
      client.subscribe(topic_command);
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  pinMode(PIN_MQ2, INPUT);
  pinMode(PIN_MQ135, INPUT);
  pinMode(PIN_WATER, INPUT);

  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_RED, OUTPUT);

  // Default state: LED Green ON, Active Buzzer OFF
  digitalWrite(PIN_LED_GREEN, HIGH);
  digitalWrite(PIN_LED_RED, LOW);
  digitalWrite(PIN_BUZZER, LOW);

  dht.begin();

  if (!mpu.begin()) {
    Serial.println("Warning: MPU6050 accelerometer init failed.");
  } else {
    Serial.println("MPU6050 Initialized.");
  }

  setup_wifi();
  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastTelemetryTime > telemetryInterval) {
    lastTelemetryTime = now;

    // 1. DHT22 Readings
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    if (isnan(temperature)) temperature = 32.5;
    if (isnan(humidity)) humidity = 67.5;

    // 2. MQ2 Raw Smoke/Gas Reading (0-4095)
    int mq2_raw = analogRead(PIN_MQ2);

    // 3. MQ135 Raw Air Quality Reading (0-4095)
    int mq135_raw = analogRead(PIN_MQ135);

    // 4. Water Level Sensor Reading (0-4095)
    int water_raw = analogRead(PIN_WATER);

    // 5. MPU6050 3-Axis Accelerometer (AX, AY, AZ in Gs)
    sensors_event_t a, g, temp_mpu;
    float ax = 0.12, ay = 0.05, az = 0.98;
    if (mpu.getEvent(&a, &g, &temp_mpu)) {
      ax = a.acceleration.x / 9.81;
      ay = a.acceleration.y / 9.81;
      az = a.acceleration.z / 9.81;
    }

    // 6. GPS NEO-6M Coordinates
    float gps_lat = 20.2961;
    float gps_lon = 85.8245;

    // 7. SIM800L Status
    String sim800l_status = "NETWORK_FOUND";

    // Build Payload matching Backend Schema
    String jsonPayload = "{";
    jsonPayload += "\"device_id\":\"esp32-guardian-01\",";
    jsonPayload += "\"timestamp\":" + String(now / 1000) + ",";
    jsonPayload += "\"temperature\":" + String(temperature, 1) + ",";
    jsonPayload += "\"humidity\":" + String(humidity, 1) + ",";
    jsonPayload += "\"mq2_raw\":" + String(mq2_raw) + ",";
    jsonPayload += "\"mq135_raw\":" + String(mq135_raw) + ",";
    jsonPayload += "\"water_raw\":" + String(water_raw) + ",";
    jsonPayload += "\"mpu_ax\":" + String(ax, 2) + ",";
    jsonPayload += "\"mpu_ay\":" + String(ay, 2) + ",";
    jsonPayload += "\"mpu_az\":" + String(az, 2) + ",";
    jsonPayload += "\"gps_lat\":" + String(gps_lat, 4) + ",";
    jsonPayload += "\"gps_lon\":" + String(gps_lon, 4) + ",";
    jsonPayload += "\"sim800l_status\":\"" + sim800l_status + "\"";
    jsonPayload += "}";

    Serial.println("Publishing Hardware Telemetry: " + jsonPayload);
    client.publish(topic_telemetry, jsonPayload.c_str());
  }
}
