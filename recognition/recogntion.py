import base64
import io
import re
from ctypes import Array
import tensorflow as tf
from pytesseract import pytesseract
from tensorflow.python.saved_model import tag_constants
import numpy as np
from imageio import imread_v2 as imread
from api.server import ImageEntity
import cv2

pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
def preprocess_image(image: Array = None):
    if image is None:
        return
    img = cv2.resize(image, (416, 416))
    img = img / 255.
    return img


class Recognizer:
    def __init__(self, path):
        self.saved_model_loaded = tf.saved_model.load(path, tags=[tag_constants.SERVING])

    def detect(self, image: ImageEntity = None) -> str:
        if image is None:
            return ""

        orig_image = self.convert_to_image(image)
        img = preprocess_image(orig_image)
        pred_bbox = self.plate_recog(img, orig_image)
        return self.ocr(cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB), pred_bbox)

    def plate_recog(self, img, orig_image):
        images_data = []
        for i in range(1):
            images_data.append(img)
        images_data = np.asarray(images_data).astype(np.float32)
        infer = self.saved_model_loaded.signatures['serving_default']
        batch_data = tf.constant(images_data)
        pred_bbox = infer(batch_data)
        for key, value in pred_bbox.items():
            boxes = value[:, :, 0:4]
            pred_conf = value[:, :, 4:]
        boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
            boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
            scores=tf.reshape(pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
            max_output_size_per_class=50,
            max_total_size=50,
            iou_threshold=0.45,
            score_threshold=0.50
        )
        original_h, original_w, _ = orig_image.shape
        bboxes = self.format_boxes(boxes.numpy()[0], original_h, original_w)
        pred_bbox = [bboxes, scores.numpy()[0], classes.numpy()[0], valid_detections.numpy()[0]]
        return pred_bbox

    @staticmethod
    def ocr(img, data):
        boxes, scores, classes, num_objects = data
        for i in range(num_objects):
            xmin, ymin, xmax, ymax = boxes[i]
            box = img[int(ymin) - 5:int(ymax) + 5, int(xmin) - 5:int(xmax) + 5]

            plate_num = ""
            gray = cv2.cvtColor(box, cv2.COLOR_RGB2GRAY)
            gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            gray = cv2.medianBlur(gray, 3)
            ret, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
            rect_kern = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            dilation = cv2.dilate(thresh, rect_kern, iterations=1)
            contours, hierarchy = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            sorted_contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])
            im2 = gray.copy()
            for cnt in sorted_contours:
                x, y, w, h = cv2.boundingRect(cnt)
                height, width = im2.shape
                if height / float(h) > 6: continue
                ratio = h / float(w)
                if ratio < 1.5: continue
                area = h * w
                if width / float(w) > 15: continue
                if area < 100: continue
                rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
                roi = thresh[y - 5:y + h + 5, x - 5:x + w + 5]
                roi = cv2.bitwise_not(roi)
                roi = cv2.medianBlur(roi, 5)
                text = pytesseract.image_to_string(roi,
                                                   config='-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ --psm 8 --oem 3')
                text = re.sub('[^a-zA-Z0-9]*', '', text, 0, re.I)
                plate_num += text
            return plate_num

    @staticmethod
    def format_boxes(bboxes, image_height, image_width):
        for box in bboxes:
            ymin = int(box[0] * image_height)
            xmin = int(box[1] * image_width)
            ymax = int(box[2] * image_height)
            xmax = int(box[3] * image_width)
            box[0], box[1], box[2], box[3] = xmin, ymin, xmax, ymax
        return bboxes

    @staticmethod
    def convert_to_image(image: ImageEntity = None):
        if image is None:
            return
        img = imread(io.BytesIO(base64.b64decode(image.image)))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img
