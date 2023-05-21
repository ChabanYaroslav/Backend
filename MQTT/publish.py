import json

import MQTT.mqtt_connection as connection


def publish_massage(topic: str, message: json):
    client = connection.connect_to_broker()
    client.publish(topic, message)
    client.disconnect()