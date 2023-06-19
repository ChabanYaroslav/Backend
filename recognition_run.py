import base64
import datetime

from recognition.recogntion import Recognizer
from api.server import ImageEntity
if __name__ == '__main__':
    detecter = Recognizer('./recognition/yolo_model/custom-416')
    image64 = ""
    with open('./recognition/testimages/car1.jpg', "rb") as img_file:
        image64 = base64.b64encode(img_file.read())
    image = ImageEntity(datetime.datetime.now(), image64)
    text = detecter.detect(image)
    print(text)

