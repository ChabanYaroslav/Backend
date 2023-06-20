import base64
import json
import logging
import string
import time

from flask import Flask, jsonify, request, Response
from flask_restful import Resource, Api, abort
from abc import abstractmethod
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
import datetime
from dateutil import parser

from database import API_DB as api_db
from mqtt import API_MQTT as api_mqtt


class Plate:

    def __init__(self, plate: string, expireDate: datetime.datetime):
        self.plate = plate
        if isinstance(expireDate, str):
            expireDate = parser.parse(expireDate)
        self.expireDate = expireDate

    def to_json(self):
        return {
            "plate": self.plate,
            "expireDate": self.expireDate.isoformat()
        }


class ImageEntity:
    def __init__(self, image_id: datetime.datetime, image: str):
        if isinstance(image_id, str):
            image_id = parser.parse(image_id)
        self.id = image_id
        self.image = image


class Log:
    def __init__(self, timestamp: datetime.datetime, action: string, description: string,
                 image: datetime.datetime | None):
        if isinstance(timestamp, str):
            timestamp = parser.parse(timestamp)
        self.timestamp = timestamp
        self.action = action
        self.description = description
        self.image = image

    def to_json(self):
        image = None
        if self.image is not None:
            image = self.image.isoformat()
        return {
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "description": self.description,
            "image": image,
        }


class Actor:
    def __init__(self, light: int = -1, bar: int = -1):
        if isinstance(light, str):
            self.light = int(light)
        else:
            self.light = light
        if isinstance(bar, str):
            self.bar = int(bar)
        else:
            self.bar = bar

    def to_json(self):
        return {
            "light": self.light,
            "bar": self.bar,
        }


class IDatabase:
    # getAllLogs returns all logs in the databases encoded in an array.
    @abstractmethod
    def getAllLogs(self) -> list[Log]:
        pass

    # getAllPlates returns all plates in the database encoded in an array.
    @abstractmethod
    def getAllPlates(self) -> list[Plate]:
        pass

    # addPlate takes a new Plate and adds it to the database. If a plate with the same ID already exists,
    # this plate is given back without actually updating it.
    @abstractmethod
    def addPlate(self, plate: Plate) -> None | Plate:
        pass

    # remPlate deletes a plate from the database. If the process was successful, return true, otherwise return false.
    @abstractmethod
    def remPlate(self, plate_id: string) -> bool:
        pass

    # remPlate updates a plate in the database. If the process was successful, return true, otherwise return false.
    @abstractmethod
    def updatePlate(self, plate_id: string, plate: Plate) -> bool:
        pass

    # getImage gets an image from the database and returns an ImageEntity.
    @abstractmethod
    def getImage(self, image_id: datetime) -> None | ImageEntity:
        pass


class IDevice:
    # getImage requests an Image from a device and returns an Image Entity with the timestamp and the base64 string.
    @abstractmethod
    def getImage(self) -> ImageEntity:
        pass

    # getSystemState request the current state from a device and returns an Actor object.
    @abstractmethod
    def getSystemState(self) -> Actor:
        pass

    # setStates allows to set the states on the device. Returns true when operation was successful, false otherwise.
    @abstractmethod
    def setStates(self, states: Actor) -> bool:
        pass


class MemoryDevice(IDevice):
    def __init__(self):
        self.image64 = None
        self.light = 0
        self.bar = 0
        self.getImageBase64("./files/testimage.jpeg")

    def getImage(self) -> ImageEntity:
        ent = ImageEntity(datetime.datetime.now(), self.image64)
        return ent

    def getSystemState(self) -> Actor:
        a = Actor(self.light, self.bar)
        return a

    def setStates(self, states: Actor) -> bool:
        if states.light >= 0:
            self.light = states.light
        if states.bar >= 0:
            self.bar = states.bar
        return True

    def getImageBase64(self, path: str):
        with open(path, "rb") as img_file:
            self.image64 = base64.b64encode(img_file.read())


class MemoryDatabase(IDatabase):
    now: datetime = None
    logs = []
    plates = []
    images = []

    dummyImage = bytearray()

    def __init__(self):
        MemoryDatabase.now = datetime.datetime.now()
        MemoryDatabase.plates = [Plate("L2776XY", MemoryDatabase.now + datetime.timedelta(hours=10)),
                                 Plate("A2122UH", MemoryDatabase.now + datetime.timedelta(days=10)),
                                 Plate("H7742L", MemoryDatabase.now + datetime.timedelta(days=100))]
        MemoryDatabase.logs = [
            Log(MemoryDatabase.now - datetime.timedelta(hours=1), "Open Bar", "The Bar opened.", None),
            Log(MemoryDatabase.now - datetime.timedelta(minutes=30), "Close Bar", "The Bar was closed",
                MemoryDatabase.now - datetime.timedelta(minutes=30))]
        self.getImageBase64("./files/testimage.jpeg")

    def getAllLogs(self) -> list[Log]:
        return MemoryDatabase.logs

    def getAllPlates(self) -> list[Plate]:
        return MemoryDatabase.plates

    def addPlate(self, plate: Plate) -> None | Plate:
        for p in MemoryDatabase.plates:
            if p.plate == plate.plate:
                return p

        MemoryDatabase.plates.append(plate)
        return None

    def remPlate(self, plate_id: string) -> bool:
        for p in MemoryDatabase.plates:
            if p.plate == plate_id:
                MemoryDatabase.plates.remove(p)
                return True
        return False

    def updatePlate(self, plate_id: string, plate: Plate) -> bool:
        for p in MemoryDatabase.plates:
            if p.plate == plate_id:
                MemoryDatabase.plates.remove(p)
                MemoryDatabase.plates.append(plate)
                return True
        return False

    def getImage(self, image_id: string) -> None | ImageEntity:
        for i in MemoryDatabase.images:
            print(i.id.isoformat())
            if i.id.isoformat() == image_id:
                return i
        return None

    def getImageBase64(self, path: str):
        with open(path, "rb") as img_file:
            MemoryDatabase.images.append(
                ImageEntity(MemoryDatabase.now - datetime.timedelta(minutes=30), base64.b64encode(img_file.read())))



################################
class Database(IDatabase):

    def __init__(self):
        pass  # do nothing

    def getAllLogs(self) -> list[Log]:
        list = []
        # time.sleep(3)
        logs = api_db.get_all_logs()
        if logs is None:
            return None

        for i in range(0, len(logs)):
            log = logs[i]
            time_id = log[0]  # datatime
            action = log[1]
            desc = log[2]
            photo_id = log[3]  # datatime
            list.append(Log(time_id, action, desc, photo_id))

        return list

    def getAllPlates(self) -> list[Plate]:
        list = []
        plates = api_db.get_all_licenses()
        if len(plates) == 0:
            return None

        for i in range(0, len(plates)):
            p = plates[i]
            number = p[0]
            date = p[1]
            list.append(Plate(number, date))

        return list

    def addPlate(self, plate: Plate) -> None | Plate:
        # check if it exists in database
        is_pl_in_db = api_db.get_license(plate.plate)
        if len(is_pl_in_db) > 0:
            return plate
        else:
            api_db.record_license(plate.plate, plate.expireDate)
            return None

    def remPlate(self, plate_id: str) -> bool:
        result = api_db.remove_license(plate_id)
        if result is None:
            return False
        else:
            return True

    def updatePlate(self, plate_id: str, plate: Plate) -> bool:
        result = api_db.change_license(plate.plate, plate.expireDate, plate_id)
        if result is None:
            return False
        else:
            return True

    def getImage(self, image_id: str) -> None | ImageEntity:
        try:
            image_id = image_id[:19]
            image_id = datetime.datetime.strptime(image_id, "%Y-%m-%dT%H:%M:%S")
            image = api_db.get_image(image_id)
        except Exception as e:
            print(e)
        if image is None or len(image) == 0:
            return None
        else:
            return ImageEntity(image_id, image)

    def getImageBase64(self, path: str):
        with open(path, "rb") as img_file:
            Database.images.append(
                ImageEntity(Database.now - datetime.timedelta(minutes=30), base64.b64encode(img_file.read())))


class Device(IDevice):
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
####################################################################


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    database = providers.Singleton(
        Database,
    )
    device = providers.Singleton(
        Device
    )


class PlatesResolver(Resource):

    # Returns all plates in the database
    @inject
    def post(self, database: IDatabase = Provide[Container.database]):
        plates = []
        data = request.get_json(force=True)
        for d in data:
            try:
                p = database.addPlate(Plate(**d))
                if p is not None:
                    plates.append(p)
            except Exception as ex:
                logging.error(ex)
        if len(plates) > 0:
            return Response(json.dumps([p.to_json() for p in plates]), status=400, mimetype='application/json')
        else:
            return "OK"

    # Gets multiple plates in the body of the request and adds it to the database.
    @inject
    def get(self, database: IDatabase = Provide[Container.database]):
        try:
            plates = database.getAllPlates()
            return jsonify([p.to_json() for p in plates])
        except Exception as ex:
            logging.error(ex)
            abort(500)


class PlateResolver(Resource):
    # Deletes a specific plate from the database
    @inject
    def delete(self, plate_id, database: IDatabase = Provide[Container.database]):
        result = False
        try:
            result = database.remPlate(plate_id)
        except Exception as ex:
            logging.error(ex)
            abort(500)

        if not result:
            abort(404)
        else:
            return "OK"

    @inject
    def post(self, plate_id, database: IDatabase = Provide[Container.database]):
        result = False
        try:
            j = request.get_json(force=True)
            plate = Plate(**j)
            result = database.updatePlate(plate_id, plate)
        except Exception as ex:
            logging.error(ex)
            abort(500)
        if not result:
            abort(404)
        else:
            return "OK"


class CurrentImageResolver(Resource):
    @inject
    def get(self, device: IDevice = Provide[Container.device]):
        try:
            i = device.getImage()
            i = i.image
            if len(str(i).split('\'')) > 1:
                base64string = 'data:image/jpeg;base64,' + str(i).split('\'')[1]
            else:
                base64string = 'data:image/jpeg;base64,' + str(i)
            return {
                "imagedata": base64string
            }
        except Exception as ex:
            logging.error(ex)
            abort(500)


class LogsResolver(Resource):
    @inject
    def get(self, database: IDatabase = Provide[Container.database]):
        try:
            logs = database.getAllLogs()
            return jsonify([l.to_json() for l in logs])
        except Exception as ex:
            logging.error(ex)
            abort(500)


class ImageResolver(Resource):
    @inject
    def get(self, image_id, database: IDatabase = Provide[Container.database]):
        result = None
        try:
            result = database.getImage(image_id)

        except Exception as ex:
            logging.error(ex)
            abort(500)

        if result is not None:
            base64string = 'data:image/jpeg;base64,' + str(result.image).split('\'')[1]
            return {
                "imagedata": base64string
            }
        else:
            abort(404)


class ActorsResolver(Resource):
    @inject
    def get(self, device: IDevice = Provide[Container.device]):
        try:
            state = device.getSystemState()
            return jsonify(state.to_json())
        except Exception as ex:
            logging.error(ex)
            abort(500)

    @inject
    def post(self, device: IDevice = Provide[Container.device]):
        try:
            j = request.get_json(force=True)
            a = Actor(**j)
            s = device.setStates(a)
            if s is None:  # if not s:
                abort(400)
            return s
        except Exception as ex:
            logging.error(ex)
            abort(500)


def run(port: int = 5000, debug: bool = False):
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(PlatesResolver, "/api/plate")
    api.add_resource(PlateResolver, "/api/plate/<plate_id>")

    api.add_resource(CurrentImageResolver, "/api/image")
    api.add_resource(ImageResolver, "/api/image/<image_id>")

    api.add_resource(LogsResolver, "/api/logs")
    api.add_resource(ActorsResolver, "/api/actors")

    container = Container()

    container.init_resources()
    container.wire(modules=[__name__])
    app.run(debug=debug, port=port, host="0.0.0.0")  # run our Flask app
