import MQTT.publish as p
import MQTT.json_message as m

topic = "SPS_2023"


def open_gate():
    message = m.json_message("0100")
    p.publish_massage(topic, message)


def close_gate():
    message = m.json_message("0101")
    p.publish_massage(topic, message)


def turn_on_light():
    message = m.json_message("0001")
    p.publish_massage(topic, message)


def turn_off_light():
    message = m.json_message("0010")
    p.publish_massage(topic, message)


def require_photo():
    message = m.json_message("0111")
    p.publish_massage(topic, message)


def get_states_of_all_actuators():
    message = m.json_message("0000")
    p.publish_massage(topic, message)


def leave_open_gate():
    message = m.json_message("0000", "12")
    p.publish_massage(topic, message)


def leave_closed_gate():
    message = m.json_message("0000", "02")
    p.publish_massage(topic, message)


def leave_on_light():
    message = m.json_message("0000", "21")
    p.publish_massage(topic, message)


def leave_off_light():
    message = m.json_message("0000", "20")
    p.publish_massage(topic, message)


def leave_open_gate_and_on_light():
    message = m.json_message("0000", "11")
    p.publish_massage(topic, message)


def leave_closed_gate_and_off_light():
    message = m.json_message("0000", "00")
    p.publish_massage(topic, message)


def reset_gate_and_light():
    message = m.json_message("0000", "22")
    p.publish_massage(topic, message)
