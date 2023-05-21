import MQTT.publish as p
import MQTT.json_message as m

# TODO: change action of message and topic

topic = "Test"


def open_gate():
    message = m.json_message(1)
    p.publish_massage(topic, message)


def close_gate():
    message = m.json_message(2)
    p.publish_massage(topic, message)


def turn_on_light():
    message = m.json_message(3)
    p.publish_massage(topic, message)


def turn_off_light():
    message = m.json_message(4)
    p.publish_massage(topic, message)


def require_photo():
    message = m.json_message(5)
    p.publish_massage(topic, message)

def get_states_of_all_actuators():
    message = m.json_message(5)
    p.publish_massage(topic, message)
