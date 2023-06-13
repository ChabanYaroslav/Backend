"""API to publish the messages to RBI"""
import datetime

import MQTT.publish as PUBL
import message.json_message as JSON_M
import DataBase.API_DB as DB

topic = "SPS_2023"


def open_gate():
    message = JSON_M.json_message("0100")
    PUBL.publish_massage(topic, message)
    DB.record_log(datetime.datetime.now(), "send command: \"open gate\"")


def close_gate():
    message = JSON_M.json_message("0101")
    PUBL.publish_massage(topic, message)
    DB.record_log(datetime.datetime.now(), "send command: \"close gate\"")


def turn_on_light():
    message = JSON_M.json_message("0001")
    PUBL.publish_massage(topic, message)
    DB.record_log(datetime.datetime.now(), "send command: \"turn on light\"")


def turn_off_light():
    message = JSON_M.json_message("0010")
    PUBL.publish_massage(topic, message)
    DB.record_log(datetime.datetime.now(), "send command: \"turn off light\"")


def require_photo():
    message = JSON_M.json_message("0111")
    PUBL.publish_massage(topic, message)
    DB.record_log(datetime.datetime.now(), "send command: \"take photo\"")


def get_states_of_all_actuators():
    message = JSON_M.json_message("0000")
    PUBL.publish_massage(topic, message)
    DB.record_log(datetime.datetime.now(), "send command: \"get all states\"")


def leave_open_gate():
    message = JSON_M.json_message("0000", "12")
    PUBL.publish_massage(topic, message)
    DB.record_log(datetime.datetime.now(), "send command: \"leave open gate\"")


def leave_closed_gate():
    message = JSON_M.json_message("0000", "02")
    PUBL.publish_massage(topic, message)
    DB.record_log(datetime.datetime.now(), "send command: \"leave close gate\"")


def leave_on_light():
    message = JSON_M.json_message("0000", "21")
    PUBL.publish_massage(topic, message)
    DB.record_log(datetime.datetime.now(), "send command: \"leave on light\"")


def leave_off_light():
    message = JSON_M.json_message("0000", "20")
    PUBL.publish_massage(topic, message)
    DB.record_log(datetime.datetime.now(), "send command: \"leave off light\"")


def leave_open_gate_and_on_light():
    message = JSON_M.json_message("0000", "11")
    PUBL.publish_massage(topic, message)
    DB.record_log(datetime.datetime.now(), "send command: \"leave open gate and on light\"")


def leave_closed_gate_and_off_light():
    message = JSON_M.json_message("0000", "00")
    PUBL.publish_massage(topic, message)
    DB.record_log(datetime.datetime.now(), "send command: \"leave closed gate and off light\"")


def reset_gate_and_light():
    message = JSON_M.json_message("0000", "22")
    PUBL.publish_massage(topic, message)
    DB.record_log(datetime.datetime.now(), "send command: \"reset state of gate and light\"")
