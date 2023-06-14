from threading import Thread

from api.server import run
from mqtt.mqtt_subscriber import run as run_subscriber

if __name__ == '__main__':
    t = Thread(target=run)
    t.start()

    t2 = Thread(target=run_subscriber)
    t2.start()

    t.join()
    t2.join()