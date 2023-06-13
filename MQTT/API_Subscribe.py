import base64

import MQTT.mqtt_connection as connection

def receive_photo() -> base64:
    client = connection.connect_to_broker()
    client.loop_start()

    while True:
        client.on_message = on_message
        time.sleep(0.5)

    # stop subscribe
    client.loop_stop()
    client.disconnect()
    pass
