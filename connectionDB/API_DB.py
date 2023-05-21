""" API to communication with DBs """
from datetime import datetime
import connectionDB.DB as DB


def connect():
    """create connection with DB"""
    DB.connect()


def close_connection():
    """close connection with DB"""
    DB.close_connection()


def get_license(license_plate: str) -> (str, str):
    """get license with its expiry_date, else given license
        does not exist in DB return value is None"""
    return DB.get_license(license_plate)


def record_license(license_plate: str, expiry_date: str):
    """record given license"""
    DB.record_license(license_plate, expiry_date)


def get_log(time_stamp: datetime, by: str):
    """get log by: year-month-day or year-month-day-hour and if by is None get all logs

    by can have only three values:
    1. "year-month-day"
    2. "year-month-day-hour"
    3. None """
    return DB.get_log(time_stamp, by)


def record_log(time_stamp: datetime, action: str, description: str, time_stamp_of_image: datetime = None):
    """record log
    image_id can be None"""
    DB.record_log(time_stamp, action, description, time_stamp_of_image)


def get_image(id: datetime):
    """get image as raw data
    to save image as jpg you have to write:

    with open('image.jpg', 'wb') as f:
        f.write(data)"""
    return DB.get_image(id)


def save_image(time_stamp: datetime, image):
    """save image in DB"""
    DB.save_image(time_stamp, image)

def record_log_with_image(time_stamp: datetime, action: str, description: str, image):
    DB.save_image(time_stamp, image)
    DB.record_log(time_stamp, action, description, time_stamp)