import json
import threading
import paho.mqtt.client as mqtt
from typing import Optional, Callable
from app.config import settings

class MQTTManager:
    """
    Manages MQTT connection to the IoT sensor node (ESP32).
    Subscribes to telemetry and publishes hardware control commands.
    """
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.connected = False
        self.on_telemetry_callback: Optional[Callable] = None

    def start(self, telemetry_callback: Callable):
        self.on_telemetry_callback = telemetry_callback
        
        try:
            # Use MQTT v3.1.1 for broad compatibility with brokers and microcontrollers
            self.client = mqtt.Client(client_id="guardian_backend_service")
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            
            # Connect in a non-blocking background thread
            thread = threading.Thread(target=self._connect_thread, daemon=True)
            thread.start()
        except Exception as e:
            print(f"[MQTT] Init warning: {e}")

    def _connect_thread(self):
        try:
            print(f"[MQTT] Connecting to broker {settings.MQTT_BROKER}:{settings.MQTT_PORT}...")
            self.client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, keepalive=60)
            self.client.loop_forever()
        except Exception as e:
            print(f"[MQTT] Connection failed (running in offline HTTP/WebSocket mode): {e}")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print(f"[MQTT] Connected successfully! Subscribing to {settings.MQTT_TOPIC_TELEMETRY}")
            client.subscribe(settings.MQTT_TOPIC_TELEMETRY)
        else:
            print(f"[MQTT] Connection returned code {rc}")

    def _on_message(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode("utf-8")
            data = json.loads(payload_str)
            print(f"[MQTT] Received Telemetry: Smoke={data.get('smoke_ppm')} Temp={data.get('temperature')}")
            if self.on_telemetry_callback:
                self.on_telemetry_callback(data)
        except Exception as e:
            print(f"[MQTT] Message parse error: {e}")

    def publish(self, topic: str, payload_str: str):
        if self.client and self.connected:
            try:
                self.client.publish(topic, payload_str)
                print(f"[MQTT] Published to {topic}: {payload_str}")
            except Exception as e:
                print(f"[MQTT] Publish error: {e}")

mqtt_manager = MQTTManager()
