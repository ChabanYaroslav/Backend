import datetime
import connectionDB.API_DB as db

db.connect()

result = db.get_license("W24681R")
print(result)

result = db.record_license("Test4", "2024-06-06")
print(result)

result = db.get_log(datetime.date(2023, 5, 16), by="year-month-day")
print(result)

result = db.record_log(datetime.date.today(), "Test", "Test", None)
print(result)

#TODO: test get ans save image

db.close_connection()
