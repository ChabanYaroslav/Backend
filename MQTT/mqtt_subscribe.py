import base64
import datetime
import time
from threading import Thread

import message.json_message as json_m
import MQTT.mqtt_connection as connection
import DataBase.API_DB as api_db
from api.server import ImageEntity
from recognition.recogntion import Recognizer


def on_message(client, userdata, messager):
    timestamp = datetime.datetime.today()
    m = json_m.loads(messager.payload.decode("utf-8"))
    action = m["action"]
    body = m["body"]  # this should be in base64

    if action == "1001":  # receive photo if car is in front of the gate
        if len(body) <= 0:
            print("Error: body is empty by receiving of photo")
            return

        # save image in DataBase #db.save_image(timestamp, body)
        Thread(target=api_db.record_log_with_image,
               args=[timestamp, "receive photo", "got photo of car from RBI", body]).start()

        global access_thread
        access_thread = Thread(target=publish_command, args=[timestamp, body]).start()


def publish_command(timestamp:datetime, image64: base64):
    number = None; expiry_date = None
    detecter = Recognizer('./recognition/yolo_model/custom-416')
    image = ImageEntity(timestamp, image64)
    plate_number_d = detecter.detect(image) # get number of plate

    result = api_db.get_license(plate_number_d)

    if len(result) != 0:
        number = result[0][0] # plate number
        expiry_date = result[0][1]
        if plate_number_d == number:
            now = datetime.datetime.now()
            if expiry_date > now:
                pass # send open gate
            else:
                pass # record log no access, expiry_date is not valid
    else:
        pass  # record log no access, plate has not permission

access_thread = None
# start subscribe
client = connection.connect_to_broker()
client.loop_start()

while True:
    client.on_message = on_message
    time.sleep(0.5)


# stop subscribe
client.loop_stop()

access_thread.join()  # we have to wait for permission deciding
client.disconnect()

