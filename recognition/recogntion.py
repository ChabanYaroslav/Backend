import base64
import io
import re
from ctypes import Array

import imutils
import tensorflow as tf
from PIL import Image
from pytesseract import pytesseract
from tensorflow.python.saved_model import tag_constants
import numpy as np
from imageio import imread_v2 as imread
from api.server import ImageEntity
import cv2
import pyocr
def preprocess_image(image: Array = None):
    if image is None:
        return
    img = cv2.resize(image, (416, 416))
    img = img / 255.
    return img


class Recognizer:
    def __init__(self, path):
        #self.saved_model_loaded = tf.saved_model.load(path, tags=[tag_constants.SERVING])
        pass

    def detect(self, image: ImageEntity = None) -> str:

        plate = self.ocr(self.convert_to_image(image))
        return plate

    def ocr(self, img):
        lab= cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l_channel, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=0.1, tileGridSize=(1,1))
        cl = clahe.apply(l_channel)

        limg = cv2.merge((cl,a,b))

        img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        img = cv2.resize(img, (1920,1080) )
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imshow('Grayscale Image',gray)


        edged = cv2.Canny(gray, 30, 200)
        cv2.imshow('Edged',edged)
        cv2.waitKey(0)
        contours = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        contours = sorted(contours, key = cv2.contourArea, reverse = True)[:30]
        screenCnt = None

        for c in contours:

            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.018 * peri, True)


            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                hwratio = float(h)/w
                ratio= float(w)/h
                if ratio>=0.9 and ratio<=1.1 and hwratio <=4 and hwratio >= 6:
                    pass
                else:

                    screenCnt = approx
                    break

        if screenCnt is None:
            detected = 0
            print ("No contour detected")
        else:
            detected = 1

        if detected == 1:
            cv2.drawContours(img, [screenCnt], -1, (0, 0, 255), 3)

        mask = np.zeros(gray.shape,np.uint8)
        new_image = cv2.drawContours(mask,[screenCnt],0,255,-1,)
        new_image = cv2.bitwise_and(img,img,mask=mask)

        (x, y) = np.where(mask == 255)
        (topx, topy) = (np.min(x), np.min(y))
        (bottomx, bottomy) = (np.max(x), np.max(y))
        Cropped = img[topx:bottomx+1, topy:bottomy+1]
        cv2.imshow("Cropped", Cropped)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


        rect = cv2.minAreaRect(screenCnt)
        box = cv2.boxPoints(rect)
        scale = 1
        W = rect[1][0]
        H = rect[1][1]

        Xs = [i[0] for i in box]
        Ys = [i[1] for i in box]
        x1 = min(Xs)
        x2 = max(Xs)
        y1 = min(Ys)
        y2 = max(Ys)

        angle = rect[2]
        rotated = False
        if angle < -45:
            angle += 90
            rotated = True

        center = (int((x1+x2)/2), int((y1+y2)/2))
        size = (int(scale*(x2-x1)), int(scale*(y2-y1)))

        M = cv2.getRotationMatrix2D((size[0]/2, size[1]/2), angle, 1.0)

        cropped = cv2.getRectSubPix(img, size, center)
        cropped = cv2.warpAffine(cropped, M, size)

        croppedW = W if not rotated else H
        croppedH = H if not rotated else W

        image = cv2.getRectSubPix(
            cropped, (int(croppedW*scale), int(croppedH*scale)), (size[0]/2, size[1]/2))

        cv2.imshow("Cropped", image)
        cv2.waitKey(0)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thres = cv2.threshold(image, 67, 255,0)
        kernel = np.ones((5, 5), np.uint8)
        cv2.erode(thres, kernel, thres)
        cv2.dilate(thres, kernel, thres)



        cv2.imshow("Img", thres)
        cv2.waitKey(0)
        cv2.imwrite("image.png", thres)
        text = pytesseract.image_to_string(thres, config="--psm 7 tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        text = re.sub('[^a-zA-Z0-9]*', '', text, 0, re.I)
        return text
    def convert_to_image(self, image: ImageEntity = None):
        if image is None:
            return
        img = imread(io.BytesIO(base64.b64decode(image.image)))

        return img