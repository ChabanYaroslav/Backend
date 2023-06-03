import base64
import time

import paho.mqtt.client as mqtt
import message.json_message as m

mqtt_broker = 'mqtt.eclipseprojects.io'
client = mqtt.Client("SPS_BACKEND_PUBLISH") # Name
client.connect(mqtt_broker)

encoded_image = None
path_image = "..//images_of_license//KU791XR.jpg"

with open(path_image, 'rb') as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

message = m.json_message("1000", encoded_image)
while True:
    message = m.json_message("1000", encoded_image)
    client.publish("SPS_2023", message) # Topic calls Test
    print("Topic Test was published: ", message)
    message = m.json_message("1111", "1111")
    client.publish("SPS_2023", message)
    time.sleep(4)

