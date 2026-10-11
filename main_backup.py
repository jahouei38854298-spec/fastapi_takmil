# python -m uvicorn main:app --reload


import json

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field


app = FastAPI()

templates = Jinja2Templates(directory="templates")


class Student(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    age: int = Field(ge=0, le=120)







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






@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"students": students}
    )


@app.post("/students/{name}/delete")
def delete_student_from_page(name: str):

    for student in students:

        if student["name"] == name:

            students.remove(student)

            save_students()

            return RedirectResponse(
                url="/",
                status_code=303
            )

    raise HTTPException(
        status_code=404,
        detail="student not found"
    )



@app.get("/students")
def get_students(
    name: str | None = None,
    age: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort: str | None = Query(
        default=None,
        pattern="^(name|name_desc|age|age_desc)$"
    )
):

    result = students.copy()

    if name is not None:
        result = [
            student
            for student in result
            if name.lower() in student["name"].lower()
        ]

    if age is not None:
        result = [
            student
            for student in result
            if student["age"] == age
        ]

    if sort == "name":
        result = sorted(
            result,
            key=lambda student: student["name"].lower()
        )

    if sort == "name_desc":
        result = sorted(
            result,
            key=lambda student: student["name"].lower(),
            reverse=True
        )

    if sort == "age":
        result = sorted(
            result,
            key=lambda student: student["age"]
        )

    if sort == "age_desc":
        result = sorted(
            result,
            key=lambda student: student["age"],
            reverse=True
        )

    total = len(result)

    students_page = result[skip:skip + limit]

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "students": students_page
    }






@app.get("/students/{name}")
def get_student(name: str):

    for student in students:

        if student["name"] == name:
            return student

    raise HTTPException(
        status_code=404,
        detail="student not found"
    )







@app.post("/students")
def create_student(student: Student):

    for existing_student in students:

        if existing_student["name"] == student.name:
            raise HTTPException(
                status_code=400,
                detail="student already exists"
            )

    students.append(student.model_dump())

    save_students()

    return student







@app.put("/students/{name}")
def update_student(name: str, student: Student):

    for existing_student in students:

        if existing_student["name"] == name:

            existing_student["age"] = student.age

            save_students()

            return existing_student

    raise HTTPException(
        status_code=404,
        detail="student not found"
    )







@app.delete("/students/{name}")
def delete_student(name: str):

    for student in students:

        if student["name"] == name:

            students.remove(student)

            save_students()

            return {
                "message": "student deleted"
            }

    raise HTTPException(
        status_code=404,
        detail="student not found"
    )