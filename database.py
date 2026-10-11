
from pymongo import MongoClient

# اتصال به MongoDB محلی
client = MongoClient("mongodb://localhost:27017/")

# انتخاب دیتابیس پروژه
db = client["fastapi_db"]

# انتخاب مجموعه کاربران
students_collection = db["students"]
