""" API to communicate with DataBase """
import base64
from datetime import datetime
import DataBase.DB as db


def connect():
    """create connection with DataBase"""
    db.connect()


def close_connection():
    """close connection with DataBase"""
    db.close_connection()


def get_license(license_plate: str) -> []:
    """get license with its expiry_date, else given license
        does not exist in DataBase return value is None"""
    return db.get_license(license_plate)



def record_license(license_plate: str, expiry_date: str) -> []:
    """record given license"""
    db.record_license(license_plate, expiry_date)


def get_all_licenses() -> []:
    return db.get_all_licenses()


def get_log(time_stamp: datetime, by: str) -> []:
    """get log by: year-month-day or year-month-day-hour and if by is None get all logs

    by can have only three values:
    1. "year-month-day"
    2. "year-month-day-hour"
    3. None """
    return db.get_log(time_stamp, by)


def get_all_logs() -> []:
    return db.get_all_logs()


def record_log(time_stamp: datetime, action: str, description: str = "", time_stamp_of_image: datetime = None) -> []:
    """record log
    image_id can be None"""
    return db.record_log(time_stamp, action, description, time_stamp_of_image)


def get_image(id: datetime) -> base64:
    """get image as base64 data """
    return db.get_image(id)


#def get_all_images()  -> []:
#    return db.get_all_images()


def save_image(time_stamp: datetime, image: base64)  -> []:
    """save image in database"""
    return db.save_image(time_stamp, image)


def record_log_with_image(time_stamp: datetime, action: str, description: str, image) -> []:
    db.save_image(time_stamp, image)
    db.record_log(time_stamp, action, description, time_stamp)


def change_license(new_license: str, expire_date: datetime,  old_license: str) -> []:
    """If the process was successful, return [], otherwise return None."""
    return db.change_license(new_license, expire_date,  old_license)


def get_license_by_substring(sublicense: str) -> []:
    return db.get_license_by_substring(sublicense)


def remove_license(plate_id: str) -> []:
    """ If the process was successful, return [], otherwise return None"""
    return db.remove_license(plate_id)