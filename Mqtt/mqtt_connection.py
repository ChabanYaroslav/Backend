"""create connection with the broker"""
import paho.mqtt.client as mqtt

client = None
mqtt_broker = 'Mqtt.eclipseprojects.io'
name_of_client = "SPS_BACKEND"
topic = "SPS_2023"


def connect_to_broker():
    """create connection with broker
        with topic
    return client"""
    global client
    try:
        client = mqtt.Client(name_of_client)
        client.connect(mqtt_broker)
        client.subscribe(topic)
        print("Mqtt-Subscribe is connected with broker. Subscribe topic is:", topic)
    except Exception as e:
        print("Error by connection with broker: ", e)
        client = None
    finally:
        return client


