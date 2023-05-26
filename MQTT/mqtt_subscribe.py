import base64
import datetime
import time

import paho.mqtt.client as mqtt
import MQTT.json_message as json_m
import MQTT.mqtt_connection as connection
import connectionDB.API_DB as db

path_of_image = "../received/image/image.jpg"
path_of_json_log = "../received/states_of_rpi/states.json"


def on_message(client, userdata, messager):
    timestamp = datetime.datetime.today()
    m = json_m.loads(messager.payload.decode("utf-8"))
    print(m)
    action = m["action"]
    body = m["body"]

    match action:
        case "1000":  # receive photo
            if len(body) <= 0:
                print("Error: body is empty by receiving of photo")
                return
            # decode body in image date
            image_data = base64.b64decode(body)
            # save in DB
            db.save_image(timestamp, image_data)
            # save as jpg in folder
            with open(path_of_image, 'wb') as image_file:
                image_file.write(image_data)
        case "1001":  # state "gate open"
            pass
        case "1002":  # state "gate close"
            pass
        case "1111":  # all states
            if len(body) <= 0:
                print("Error: body is empty by receiving of all states")
                return
            # save in DB
            a = "gate "
            a = body[0] == "1" and a + "open" or a + "close"
            l = ", light "
            l = body[1] == "1" and l + "on" or l + "off"

            ls1 = "Is car in front of ls1: "
            ls1 = body[2] == "1" and ls1 + "yes" or ls1 + "no"
            ls2 = " ,Is car in front of ls2: "
            ls2 = body[3] == "1" and ls2 + "yes" or ls2 + "no"

            ac = a + l
            des = ls1 + ls2
            db.record_log(timestamp, ac, des)

            # save in folder
            with open(path_of_json_log, "w") as outfile:
                outfile.write(messager)


# start subscribe
client = connection.connect_to_broker()
client.loop_start()

while True:
    client.on_message = on_message
    time.sleep(0.5)

# stop subscribe
client.loop_stop()
client.disconnect()
