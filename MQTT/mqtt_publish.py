# Open source broker: https://mqtt.eclipseprojects.io/
import base64
import os.path
import time

import paho.mqtt.client as mqtt
import MQTT.json_message as m

mqtt_broker = 'mqtt.eclipseprojects.io'
client = mqtt.Client("SPS_BACKEND_PUBLISH") # Name
client.connect(mqtt_broker)

encoded_image = None
path_image = "..//images_of_license//W24681R.jpg"

with open(path_image, 'rb') as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

message = m.json_message(1001, encoded_image)
print(message)
while True:
    client.publish("SPS_2023", message) # Topic calls Test
    print("Topic Test was published: ", message)
    time.sleep(3)
