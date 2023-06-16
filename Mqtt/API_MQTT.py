import datetime
from threading import Thread


import Database.API_DB as db
from message import json_message as json_m
import Mqtt.mqtt_connection as connection

topic = "SPS_2023"
photo = None
timestamp = None
light = -1
bar = -1
is_set = False


def get_photo_from_rbi():
    global photo, timestamp

    def on_message(client, userdata, messager):
        global photo, timestamp, run
        timestamp = datetime.datetime.today()
        m = json_m.loads(messager.payload.decode("utf-8"))
        action = m["action"]
        body = m["body"]  # this should be in base64

        if action == "1000":  # receive photo
            if len(body) <= 0:
                print("Error: body is empty by receiving of photo")
                client.disconnect()
                return

            photo = body
            # save image in Database #db.save_image(timestamp, body)
            Thread(target=db.record_log_with_image,
                   args=[timestamp, "receive photo", "got photo from RBI", photo]).start()

            # stop subscribe
            client.disconnect()

    # end of on_message

    # log
    Thread(target=db.record_log,
           args=[datetime.datetime.now(), "request photo", "send command to RBI: \"take photo\""]).start()

    # send request
    message = json_m.json_message("0111")
    client = connection.connect_to_broker()
    client.publish(topic, message)

    # start subscribe
    client.on_message = on_message
    client.loop_forever()

    return timestamp, photo


def get_system_state_from_rbi():
    global light, bar
    light = -1
    bar = -1

    def on_message(client, userdata, messager):
        global light, bar
        timestamp = datetime.datetime.today()
        m = json_m.loads(messager.payload.decode("utf-8"))
        action = m["action"]
        body = m["body"]  # has gate,light,LS1,LS2

        if action == "1000":  # receive states
            if len(body) <= 0:
                print("Error: body is empty by receiving of all states")
                client.disconnect()
                return
            # read states of RBI
            bar = body[0]
            light = body[1]

            # create description
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
            # save in Database # db.record_log(timestamp, ac, des)
            Thread(target=db.record_log,
                   args=[timestamp, "receive states", des]).start()

            client.disconnect()  # stop subscribe

    # end of on_message

    # log
    Thread(target=db.record_log,
           args=[datetime.datetime.now(), "request states",
                 "send command to RBI: \"get states of bar and light\""]).start()

    # request all states
    message = json_m.json_message("0000")
    client = connection.connect_to_broker()
    client.publish(topic, message)

    client.on_message = on_message
    client.loop_forever()

    return light, bar


def set_system_state(light: int, bar: int) -> bool:
    global is_set
    is_set = False

    def on_message(client, userdata, messager):
        global is_set
        timestamp = datetime.datetime.today()
        m = json_m.loads(messager.payload.decode("utf-8"))
        action = m["action"]
        body = m["body"]

        if action == "1111":  # 1111 with new states with body: gate,light
            rec_bar = int(body[0])
            rec_light = int(body[1])
            if rec_bar == bar and rec_light == light:
                is_set = True
                Thread(target=db.record_log,
                       args=[timestamp, "receive answer",
                             "receive answer to request from RBI to set its states like: light: " + str(
                                 light) + "bar: " + str(bar)]).start()
            else:
                is_set = False
                Thread(target=db.record_log,
                       args=[timestamp, "receive answer",
                             "unsuccessful setting of states. Actual states are: light: " + str(
                                 rec_light) + "bar: " + str(rec_bar)]).start()
            client.disconnect()

    # end of on_message

    # 2 means that RBI can decide for itself what to do
    # 1 means open/on
    # 0 means close/off
    if bar == -1:
        bar = 2
    if light == -1:
        light == 2

    setting = str(bar) + str(light)  # "gate,light"
    # log
    Thread(target=db.record_log,
           args=[datetime.datetime.now(), "set states of RBI",
                 "send command to RBI: \" set bar: " + str(bar) + " and light: " + str(light) + "\""]).start()

    message = json_m.json_message("0000", setting)
    client = connection.connect_to_broker()
    client.publish(topic, message)

    client.on_message = on_message
    client.loop_forever()

    return is_set
