import json

from schemas.student import Student


def load_students():
    with open("students.json", "r", encoding="utf-8") as file:
        return json.load(file)


students = load_students()


def save_students():
    with open("students.json", "w", encoding="utf-8") as file:
        json.dump(
            students,
            file,
            ensure_ascii=False,
            indent=4
        )


def find_student_by_name(name: str):

    for student in students:

        if student["name"] == name:
            return student

    return None


def add_student(student: Student):

    students.append(student.model_dump())

    save_students()

    return student


def update_student(name: str, student: Student):

    for existing_student in students:

        if existing_student["name"] == name:

            existing_student["age"] = student.age

            save_students()

            return existing_student

    return None


def delete_student(name: str):

    for student in students:

        if student["name"] == name:

            students.remove(student)

            save_students()

            return True

    return False