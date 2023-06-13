import base64
import datetime
import time

import message.json_message as json_m
import MQTT.mqtt_connection as connection
import DataBase.API_DB as DB

path_of_image = "../received/image/image.jpg"
path_of_json_log = "../received/states_of_rpi/states.json"


def on_message(client, userdata, messager):
    timestamp = datetime.datetime.today()
    m = json_m.loads(messager.payload.decode("utf-8"))
    #print(m)
    action = m["action"]
    body = m["body"]
    print(action)
    print(m)

    match action:
        case "1000":  # receive photo
            if len(body) <= 0:
                print("Error: body is empty by receiving of photo")
                return
            # decode body in image date
            image_data = body #base64.b64decode(body) # TODO corr encode image
            # save in DataBase # TODO need corr format for image saving
            DB.save_image(timestamp, image_data)
            # save as jpg in folder
            image_data = base64.b64decode(body)
            with open(path_of_image, 'wb') as image_file:
                image_file.write(image_data)
        case "1111":  # all states
            if len(body) <= 0:
                print("Error: body is empty by receiving of all states")
                return
            # save in DataBase
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
            # save in DataBase
            #DB.record_log(timestamp, ac, des)

            # save json in folder
            json_m.save_to_file(m, path_of_json_log)
        case _:
            print("Error: Received message with unknown action:", action)

# start subscribe
client = connection.connect_to_broker()
client.loop_start()

while True:
    client.on_message = on_message
    time.sleep(0.5)

# stop subscribe
client.loop_stop()
client.disconnect()
