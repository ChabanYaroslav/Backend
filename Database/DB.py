"""this module provides communication with db"""
import base64
from datetime import datetime


from Database.ConnectDB import ConnectDB

# Database
conn = ConnectDB()
conn.connect()
cur = conn.get_cursor()

# name of the tables in Database
licenses_table = 'license_plates'
images_table = 'images'
logs_table = 'logs'

# queries
select = "Select {} FROM {} "
select_where = select + "WHERE {}"
insert = "insert into {} ({}) values ({})"
update = "update {} set {} = {} where {} = {}"
select_by_substring = "select {} from {} where {} = \'{}%\'"
delete_query = "DELETE FROM {} WHERE {}"


def connect():
    """create connection with Database"""
    global conn  # to change global variable
    conn = ConnectDB()
    conn.connect()
    global cur
    cur = conn.get_cursor()


def close_connection():
    global conn
    conn.close()


def get_license(license: str) -> (str, str):
    """get license with its expiry_date, else given license
    does not exist in Database return value is (-1,-1)"""
    column = "license_plate, expiry_date"
    name_of_table = licenses_table
    where_condition = "license_plate = \'" + license + "\'"

    return __get_data(column, name_of_table, where_condition)


def record_license(license: str, expiry_date: datetime):
    """record given license"""
    name_of_table = licenses_table
    column = 'license_plate, expiry_date'
    expiry_date = expiry_date.strftime("%Y-%m-%d")
    values = [license, expiry_date]

    return __insert_data(name_of_table, column, values)


def get_all_licenses():
    name_of_table = licenses_table
    column = '*'
    return __get_data(column, name_of_table)


def change_license(new_license: str, new_expire_date: datetime, old_license: str):
    name_of_table = licenses_table
    query = "update {} set license_plate = \'{}\', expiry_date = \'{}\' where license_plate = \'{}\'".format(name_of_table, new_license, new_expire_date, old_license)
    return __execute_query(query, True)


def get_license_by_substring(substring: str):
    name_of_table = licenses_table
    column = '*'
    where = 'license_plate Like \'{}%\''.format(substring)
    return __get_data(column, name_of_table, where)


def get_log(time_stamp: datetime, by: str):
    """get log by: year-month-day or year-month-day-hour and if by is None get all logs

    by can have only three values:
    1. \"year-month-day\"
    2. \"year-month-day-hour\"
    3. None """

    column = '*'  # means get all columns
    name_of_table = logs_table

    year = str(time_stamp.year)
    month = str(time_stamp.month)
    if len(month) == 1:
        month = '0' + month
    day = str(time_stamp.day)
    if len(day) == 1:
        day = '0' + day

    date = year + "-" + month + "-" + day
    where_condition = None
    if by == "year-month-day":
        where_condition = "to_char(time_stemp, 'yyyy-mm-dd') = " + "\'" + date + "\'"
    else:  # by == "year-month-day-hour"
        hour = str(time_stamp.hour)
        if len(hour) == 1:
            hour = '0' + hour

        date = date + " " + hour
        where_condition = "to_char(time_stemp, 'yyyy-mm-dd HH24') = " + "\'" + date + "\'"

    return __get_data(column, name_of_table, where_condition)


def get_all_logs():
    name_of_table = logs_table
    column = '*'
    return __get_data(column, name_of_table)


def record_log(time_stamp: datetime, action: str, description: str, time_stamp_of_image: datetime = None):
    column = "time_stemp, action, description, image_id"
    name_of_table = logs_table
    time_stamp = time_stamp.strftime("%Y-%m-%d %H:%M:%S")
    if time_stamp_of_image is None:
        time_stamp_of_image = None
    else:
        time_stamp_of_image = str(time_stamp_of_image)
    values = [time_stamp, action, description, time_stamp_of_image]

    return __insert_data(name_of_table, column, values)


def get_image(id: datetime) -> base64:
    """ get images date in base64 format """
    column = 'image_data'
    name_of_table = images_table
    where_condition = "to_char(id, 'yyyy-mm-dd HH24:MI:SS') = \'" + id.strftime("%Y-%m-%d %H:%M:%S") + "\'"
    data = __get_data(column, name_of_table, where_condition)
    data = base64.b64decode(bytes(data[0][0])) # bytes converts the address of memory to the value, that saved in this memory block
    return data


def get_all_images():
    name_of_table = images_table
    column = '*'
    return __get_data(column, name_of_table)


def save_image(time_stamp: datetime, image: base64):
    name_of_table = images_table
    column = 'id, image_data, file_extension'
    value = [str(time_stamp), image, 'jpg']
    return __insert_data(name_of_table, column, value)


# private function
def __execute_query(query: str, insert: bool) -> []:
    """execute given query and get result"""
    global conn
    global cur
    result = []
    try:
        cur.execute(query)
        if insert:
            # global curr
            conn.commit()
            result = [] # means that executing was successful
        else:  # because if insert then we get error, because db.fetchall() does not work by insert query
            result = cur.fetchall()
    except Exception as e:
        print("Error by query execution. Query: ", query)
        print("Error:", e)
        conn.rollback()
        result = None
    finally:
        return result


def __insert_data(name_of_table: str, column: str, values):
    array = ''
    for i in range(len(values)):
        val = values[i]
        if isinstance(val, str):
            val = '\'' + val + '\''
        elif val is None:
            val = 'null'
        if i + 1 < len(values):
            array = array + str(val) + ', '
        else:
            array = array + str(val)
    query = insert.format(name_of_table, column, array)
    return __execute_query(query, insert=True)


def __get_data(column: str, name_of_table: str, where_condition: str = None):
    """get data of db"""
    query = ''
    if where_condition is None:
        query = select.format(column, name_of_table)
    else:
        query = select_where.format(column, name_of_table, where_condition)
    return __execute_query(query, insert=False)


def remove_license(plate_id: str):
    where = "license_plate = \'" + str(plate_id) + '\''
    query = delete_query.format(licenses_table, where)
    return __execute_query(query, True)