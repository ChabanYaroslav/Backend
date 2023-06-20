import base64
import datetime
import time


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

    if action == "1001":  # receive photo if car is in front of the gate
        if len(body) <= 0:
            print("Error: body is empty by receiving of photo")
            return

        # save image in database
        api_db.record_log_with_image(timestamp, "receive photo", "got photo of car from RBI", body)

        # recog. image
        publish_command(timestamp, body, client)


def publish_command(timestamp: datetime, image64: base64, client):
    number = None
    expiry_date = None
    image = ImageEntity(timestamp, image64)
    plate_number_d = detecter.detect(image)  # get number of plate

    if plate_number_d is None:
        plate_number_d = ''
    else:
        print("The plate number was recognized as:", plate_number_d)

    result = api_db.get_license(plate_number_d)

    if result is not None and len(result) != 0:  # check if Databank has this plate number
        number = result[0][0]  # plate number
        expiry_date = result[0][1]
        now = datetime.date.today()
        if expiry_date >= now:
            # send open gate
            message = json_m.json_message("0001")
            client.publish(topic, message)
            api_db.record_log(timestamp, "open gate/bar", "The car has permission to drive in")
        else:
            # send keep gate close, expiry_date is not valid
            message = json_m.json_message("0010")
            client.publish(topic, message)
            api_db.record_log(timestamp, "keep gate/bar close", "No permission, expiry date of plate has expired")
    else:
        # send keep gate/bar close, plate was not found in the db
        message = json_m.json_message("0010")
        client.publish(topic, message)
        api_db.record_log(timestamp, "keep gate/bar close", "This car has no permission")


topic = "SPS_2023"
threads = []
detecter = None
client = None


def run():
    print("Subscriber runs")
    global detecter, client

    detecter = Recognizer()

    # start subscribe
    client = connection.connect_to_broker()
    client.on_message = on_message
    client.loop_start()

    while True:
        time.sleep(0.1)

    # stop subscribe
    client.loop_stop()
    client.disconnect()
