"""Action encode:

    RPI -> Backend
    N | action |       body           | meaning
    -----------------------------------------------------
    1 | 1000   |    photo data        | sends photo to BE by request from BE
    2 | 1001   |    photo data        | sends photo to BE if car is in front of the gate
      | 1002   |                      | sends answers "ok" to the request "set states" to BE
    3 | 1111   | "gate,light,LS1,LS2" | sends all states to BE
        example for 3: { action: 1111, body: "1111" }
        where in body "1" means: gate is open, light is on; LS1 and LS2 we have something in front of the sensor
                      "0" means: gate is close, light is off; LS1 and LS2 we do not have something in front of the sensor

    Backend -> RPI
     N | action |       body           | meaning
    -----------------------------------------------------
     1 | 0001  |                       | open gate ( car has permission)
     2 | 0010  |                       | keep gate close (car has no permission)
     3 | 0100  |                       |
     4 | 0101  |                       |
     5 | 0111  |                       | requests photo
    6a | 0000  |                       | requests all states
    6b | 0000  | "gate,light"          | sets state of RMI as long as it is not reset; 2 means don't care, 1 or 0 set states of RPI
        for 6b: {"action:" 0000, "21"}
        where: RPI is allowed to change gate itself
               but light should be always on
        for 6b: {"action:" 0000, "10"}
        where: Gate is always open
               Light is always off

        to reset the command 6b: {"action:" 0000, "22"}
"""
import json


def json_message(action: str, body: str = ''):
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


def save_to_file(json_message: json, path_of_file: str):
    try:
        file = open(path_of_file, "w")
        json.dump(json_message, file, indent=4)
        file.close()
    except Exception as e:
        print("Error by json saving:", e)
