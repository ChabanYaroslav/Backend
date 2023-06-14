import base64
import datetime
import string
import time
from abc import abstractmethod

import psycopg2

import DataBase.API_DB as db


class Plate:

    def __init__(self, plate: string, expireDate: datetime.datetime):
        self.plate = plate
        #if isinstance(expireDate, str):
           # expireDate = parser.parse(expireDate)
        self.expireDate = expireDate

    def to_json(self):
        return {
            "plate": self.plate,
            "expireDate": self.expireDate.isoformat()
        }


class ImageEntity:
    def __init__(self, image_id: datetime.datetime, image):
        #if isinstance(image_id, str):
           # image_id = parser.parse(image_id)
        self.id = image_id
        self.image = image


class Log:
    def __init__(self, timestamp: datetime.datetime, action: string, description: string,
                 image: datetime.datetime | None):
        #if isinstance(timestamp, str):
          #  timestamp = parser.parse(timestamp)
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
        self.light = light
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
        list = []
        logs = db.get_all_logs()
        for i in range(0, len(logs)):
            log = logs[i]
            time_id = log[0] # datatime
            action = log[1]
            desc = log[2]
            photo_id = log[3] # datatime
            list.append(Log(time_id, action, desc, photo_id))

        return list

    # getAllPlates returns all plates in the database encoded in an array.
    @abstractmethod
    def getAllPlates(self) -> list[Plate]:
        list = []
        plates = db.get_all_licenses()
        for i in range(0, len(plates)):
            p = plates[i]
            number = p[0]
            date = p[1]
            list.append(Plate(number, date))

        return list

    # addPlate takes a new Plate and adds it to the database. If a plate with the same ID already exists,
    # this plate is given back without actually updating it.
    @abstractmethod
    def addPlate(self, plate: Plate) -> None | Plate:
        # check if it exists in database
        is_pl_in_db = db.get_license(plate.plate)
        if len(is_pl_in_db) > 0:
            return plate
        else:
            db.record_license(plate.plate, plate.expireDate)


    # remPlate deletes a plate from the database. If the process was successful, return true, otherwise return false.
    @abstractmethod
    def remPlate(self, plate_id: string) -> bool:
        result = db.remove_license(plate_id)
        if result is None:
            return False
        else:
            return True


    # updatePlate updates a plate in the database. If the process was successful, return true, otherwise return false.
    @abstractmethod
    def updatePlate(self, plate_id: string, plate: Plate) -> bool:
        result = db.change_license(plate.plate, plate.expireDate, plate_id)
        if result is None:
            return False
        else:
            return True


    @abstractmethod
    def getImage(self, image_id: datetime) -> None | ImageEntity:
        image = db.get_image(image_id)
        if image is None or len(image) == 0:
            return None
        else:
            return ImageEntity(image_id, image)

db.connect()

time_now = datetime.datetime.now()
print(time_now)
given_time = datetime.datetime(2023, 6, 13,  9, 18, 58)
print(given_time)
given_time2 = datetime.date(2023, 6, 13)

d = IDatabase()

try:
    result = d.getAllLogs()
    print(result)
except Exception as e:
    print(e)

try:
    result = d.getAllPlates()
    print(result)
except Exception as e:
    print(e)

try:
    p = Plate("xxxx", given_time2)
    result = d.addPlate(p)
    print("addPlate: ", result, "should be None")
except Exception as e:
    print(e)

try:
    p = Plate("xxxx", given_time2)
    result = d.addPlate(p)
    print("double addPlate: ", result, "should be p")
except Exception as e:
    print(e)

try:
    p = Plate("xxxx", given_time2)
    result = d.updatePlate("xxxx", p)
    print("updatePlate: ", result, "should be True")
except Exception as e:
    print(e)

try:
    p = Plate("xxxx", given_time2)
    result = d.remPlate(p.plate)
    print("remove added Plate remPlate: ", result, "should be True")
except Exception as e:
    print(e)

try:
    result = d.getImage(given_time)
    print("getImage: ", result)
except Exception as e:
    print(e)



path_image = "..//images_of_license//KU791XR.jpg"
#image_file = open(path_image, 'rb')
image_file2 = open(path_image, 'rb')
image_file2 = base64.b64encode(image_file2.read()).decode('utf-8')


#db.save_image(time_now1, image_file)
print("image1")
#result = db.save_image(time_now2, image_file2)
print("image2")
result = db.get_image(datetime.datetime(2023, 6, 13,  9, 18, 58))
with open("..//images_of_license//KU791XR222222.jpg", 'wb') as image_file:
    image_file.write(result)

print("hier")
#id_image = datetime.datetime.today()
#result = db.save_image(id_image, encoded_image)
#print("save_image", result)

#result = db.get_image(id_image)
#print("get_image", result)
#print("get_image")

#result = db.get_all_images()
#print(bytes(result[0][1]))
#print(base64.b64decode(bytes(result[0])))

db.close_connection()
