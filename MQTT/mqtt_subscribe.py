import base64
import time

import paho.mqtt.client as mqtt
import MQTT.json_message as m


def on_message(client, userdata, messager):
    messager = m.loads(messager.payload.decode("utf-8"))
    print(messager)
    if len(messager) == 1:  # we got hello message from broker
        print(messager)
    else:
        action = messager["action"]
        if action == 1000:
            pass
        if action == 1001:
            body = messager["body"]
            image_data = base64.b64decode(body)
            print(image_data)
            # with open('received_image.jpg', 'wb') as image_file:
            #    image_file.write(image_data)
        print("Test: ", messager)


mqtt_broker = 'mqtt.eclipseprojects.io'
client = mqtt.Client("SPS_BACKEND_SUBSCRIBE")  # Name of client
client.connect(mqtt_broker)

client.loop_start()
client.subscribe("Test")
client.on_message = on_message
time.sleep(30)
client.loop_stop()
