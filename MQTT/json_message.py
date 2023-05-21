"""Action encode:
    for Backend (Backend receives message from RPI)
    1. 1000 - message without photo
    2. 1001 - message with photo
    for RPI (RPI receives message from Backend-Server)
    1.

"""
import json

def json_message(action: int, body: str = ''):
    """return json object"""
    message = {
                "action": action,
                "body": body
              }
    message["action"]
    return json.dumps(message)

def loads(json_message):
    """decode json object"""
    return json.loads(json_message)