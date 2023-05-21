"""create connection with the broker"""
import paho.mqtt.client as mqtt

client = None
mqtt_broker = 'mqtt.eclipseprojects.io'
name_of_client = "SPS_BACKEND_PUBLISH"


def connect_to_broker():
    """create connection with broker
    return client"""
    global client
    try:
        client = mqtt.Client(name_of_client)
        client.connect(mqtt_broker)
    except Exception as e:
        print("Error by connection with broker: ", e)
        client = None
    finally:
        return client


