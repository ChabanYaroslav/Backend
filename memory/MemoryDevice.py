import base64
from datetime import datetime

from api.server import ImageEntity, Actor, IDevice
from MQTT import API_MQTT as api_mqtt


class MemoryDevice(IDevice):
    def __init__(self):
        pass

    def getImage(self) -> ImageEntity:
        time, image_data = api_mqtt.get_photo_from_rbi()
        return ImageEntity(time, str(image_data))

    def getSystemState(self) -> Actor:
        light, bar = api_mqtt.get_system_state_from_rbi()
        return Actor(light, bar)

    def setStates(self, states: Actor) -> bool:
        is_set = api_mqtt.set_system_state(states.light, states.bar)
        return is_set
