"""Small paho-mqtt v2 helper shared by simulators, tools and services."""
import json
import os

import paho.mqtt.client as mqtt

BROKER_HOST = os.environ.get("MQTT_HOST", "localhost")
BROKER_PORT = int(os.environ.get("MQTT_PORT", "1883"))


def make_client(client_id: str, will_topic: str | None = None, will_payload: dict | None = None) -> mqtt.Client:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    if will_topic:
        client.will_set(will_topic, json.dumps(will_payload), qos=1, retain=True)
    client.reconnect_delay_set(min_delay=1, max_delay=10)
    return client


def connect(client: mqtt.Client, host: str = BROKER_HOST, port: int = BROKER_PORT) -> None:
    """Connect in the background; paho retries automatically after the first attempt."""
    client.connect_async(host, port, keepalive=15)
    client.loop_start()


def publish_json(client: mqtt.Client, topic: str, payload: dict, qos: int = 0, retain: bool = False):
    return client.publish(topic, json.dumps(payload, ensure_ascii=False), qos=qos, retain=retain)
