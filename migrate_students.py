
import json

from database import students_collection

# خواندن اطلاعات از فایل JSON
with open("students.json", "r", encoding="utf-8") as file:
    students = json.load(file)

# انتقال اطلاعات به MongoDB
if students:
    students_collection.insert_many(students)

print(f"{len(students)} students imported successfully.")
