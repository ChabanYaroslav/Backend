import datetime
import json
import time
from threading import Thread


import database.API_DB as db
from message import json_message as json_m
import mqtt.mqtt_connection as connection

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
            # save image in database #db.save_image(timestamp, body)
            db.record_log_with_image(timestamp, "receive photo", "got photo from RBI", photo)
            # stop subscribe
            client.disconnect()

    # end of on_message

    # log
    db.record_log(datetime.datetime.now(), "request photo", "send command to RBI: \"take photo\"")
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

        if action == "1111":  # receive states
            if len(body) <= 0:
                print("Error: body is empty by receiving of all states")
                client.disconnect()
                return
            # read states of RBI
            bar = body[0]
            light = body[1]

            # create description
            a = "gate is "
            a = body[0] == "1" and a + "open" or a + "close"
            l = ", light is "
            l = body[1] == "1" and l + "on" or l + "off"

            des = a + l

            # save in database
            db.record_log(timestamp, "receive states", des)
            client.disconnect()  # stop subscribe

    # end of on_message

    # log
    db.record_log(datetime.datetime.now(), "request states",
                 "send command to RBI: \"get states of bar and light\"")
    # request all states
    message = json_m.json_message("0000")
    client = connection.connect_to_broker()
    client.publish(topic, message)

    client.on_message = on_message
    client.loop_forever()

    return light, bar

rec_bar = None
rec_light = None

def set_system_state(light: int, bar: int) -> bool:
    global is_set, rec_bar, rec_light
    is_set = False

    def on_message(client, userdata, messager):
        global is_set, rec_bar, rec_light
        timestamp = datetime.datetime.today()
        m = json_m.loads(messager.payload.decode("utf-8"))
        action = m["action"]
        body = m["body"]

        if action == "1111":  # 1111 with new states with body: gate,light
            if len(body) <= 0:
                print("Error: body is empty by receiving changed states")
                client.disconnect()
                return

            rec_bar = int(body[0])
            rec_light = int(body[1])
            if rec_bar == bar and rec_light == light:
                is_set = True
                Thread(target=db.record_log,
                       args=[timestamp, "receive answer",
                             "RBIs states was set like: light:" + str(
                                 light) + " bar:" + str(bar)]).start()
            else:
                is_set = False
                Thread(target=db.record_log,
                       args=[timestamp, "receive answer",
                             "Unsucc. setting. The states stay: light:" + str(
                                 rec_light) + " bar:" + str(rec_bar)]).start()
            client.disconnect()

    # end of on_message

    # 2 means that RBI can decide for itself what to do
    # 1 means open/on
    # 0 means close/off
    if bar == 0 or bar == -1:
        bar = 2
    if light == 0 or light == -1:
        light = 2

    setting = str(bar) + str(light)  # "gate,light"
    # log
    #Thread(target=db.record_log,
    #       args=[datetime.datetime.now(), "set states of RBI",
    #             "send command to RBI:\"set bar:" + str(bar) + " and light:" + str(light) + "\""]).start()
    db.record_log(datetime.datetime.now(), "set states of RBI",
                 "send command to RBI:\"set bar:" + str(bar) + " and light:" + str(light) + "\"")
    message = json_m.json_message("0000", setting)
    client = connection.connect_to_broker()
    client.publish(topic, message)

    client.on_message = on_message
    client.loop_forever()
    j = '{"bar":'+str(rec_bar)+', "light": '+str(rec_light)+'}'
    return json.loads(j) #is_set
