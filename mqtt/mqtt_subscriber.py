import base64
import datetime
import os
import sys
import time
from threading import Thread

import message.json_message as json_m
import mqtt.mqtt_connection as connection
import database.API_DB as api_db
from api.server import ImageEntity
from recognition.recogntion import Recognizer


def on_message(client, userdata, messager):
    timestamp = datetime.datetime.today()
    m = json_m.loads(messager.payload.decode("utf-8"))
    action = m["action"]
    body = m["body"]  # this should be in base64

    if action == "1000":
        print("receive 1000")

    if action == "1001":  # receive photo if car is in front of the gate
        if len(body) <= 0:
            print("Error: body is empty by receiving of photo")
            return

        # save image in database #db.save_image(timestamp, body)
        t = Thread(target=api_db.record_log_with_image,
               args=[timestamp, "receive photo", "got photo of car from RBI", body])
        threads.append(t)
        t.start()

        t = Thread(target=publish_command, args=[timestamp, body])
        threads.append(t)
        t.start()

def publish_command(timestamp:datetime, image64: base64):
    number = None; expiry_date = None
    image = ImageEntity(timestamp, image64)
    plate_number_d = detecter.detect(image) # get number of plate

    result = api_db.get_license(plate_number_d)

    if len(result) != 0:
        number = result[0][0] # plate number
        expiry_date = result[0][1]
        if plate_number_d == number:
            now = datetime.datetime.now()
            if expiry_date >= now:
                # send open gate
                message = json_m.json_message("0001")
                client.publish(topic, message)
                t = Thread(target=api_db.record_log, args=[timestamp, "open gate/bar", "The car has permission to drive in" ])
                threads.append(t)
                t.start()
            else:
                # send leave gate close, expiry_date is not valid
                message = json_m.json_message("0010")
                client.publish(topic, message)
                t = Thread(target=api_db.record_log,
                       args=[timestamp, "keep gate/bar close", "No permission, expiry date of plate has expired"])
                threads.append(t)
                t.start()
    else:
        # send keep gate/bar close
        message = json_m.json_message("0010")
        client.publish(topic, message)
        t = Thread(target=api_db.record_log,
               args=[timestamp, "keep gate/bar close", "This car has no permission"])
        threads.append(t)
        t.start()


topic = "SPS_2023"
threads = []
detecter = None
client = None
def run():
    print("Subscriber runs")
    global  detecter, client

    detecter = Recognizer(os.path.join('.', 'recognition', 'yolo_model'))

    # start subscribe
    client = connection.connect_to_broker()
    client.loop_start()

    while True:
        client.on_message = on_message
        time.sleep(0.5)


    # we have to wait for permission deciding
    for t in threads:
        t.join()

    # stop subscribe
    client.loop_stop()
    client.disconnect()
