import base64
from datetime import datetime

from api.server import IDatabase, Log, Plate, ImageEntity
from DataBase import API_DB as api_db


class MemoryDatabase(IDatabase):

    def __init__(self):
        pass  # do nothing

    def getAllLogs(self) -> list[Log]:
        list = []
        logs = api_db.get_all_logs()
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
        image = api_db.get_image(image_id)
        if image is None or len(image) == 0:
            return None
        else:
            return ImageEntity(image_id, str(image))

    def getImageBase64(self, path: str):
        with open(path, "rb") as img_file:
            MemoryDatabase.images.append(
                ImageEntity(MemoryDatabase.now - datetime.timedelta(minutes=30), base64.b64encode(img_file.read())))


