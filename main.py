# python -m uvicorn main:app --reload





from fastapi import FastAPI, HTTPException, Query, Request, Form
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from database import students_collection
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")




def get_students_from_db():
    return list(
        students_collection.find(
            {},
            {"_id": 0}
        )
    )


class Student(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    age: int = Field(ge=0, le=120)







@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    students = get_students_from_db()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"students": students}
    )






@app.post("/students/add")
def add_student_from_page(
    name: str = Form(..., min_length=2, max_length=50),
    age: int = Form(..., ge=0, le=120)
):
    student = Student(name=name, age=age)

    existing_student = students_collection.find_one(
        {"name": student.name}
    )

    if existing_student is not None:
        raise HTTPException(
            status_code=400,
            detail="student already exists"
        )

    students_collection.insert_one(
        student.model_dump()
    )

    return RedirectResponse(
        url="/",
        status_code=303
    )






@app.post("/students/{name}/edit")
def edit_student_from_page(
    name: str,
    age: int = Form(..., ge=0, le=120)
):
    result = students_collection.update_one(
        {"name": name},
        {"$set": {"age": age}}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="student not found"
        )

    return RedirectResponse(
        url="/",
        status_code=303
    )












@app.post("/students/{name}/delete")
def delete_student_from_page(name: str):

    result = students_collection.delete_one(
        {"name": name}
    )

    if result.deleted_count == 1:
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
    result = get_students_from_db()

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

    student = students_collection.find_one(
        {"name": name},
        {"_id": 0}
    )

    if student is not None:
        return student

    raise HTTPException(
        status_code=404,
        detail="student not found"
    )









@app.post("/students")
def create_student(student: Student):

    existing_student = students_collection.find_one(
        {"name": student.name}
    )

    if existing_student is not None:
        raise HTTPException(
            status_code=400,
            detail="student already exists"
        )

    students_collection.insert_one(
        student.model_dump()
    )

    return student








@app.put("/students/{name}")
def update_student(name: str, student: Student):

    result = students_collection.update_one(
        {"name": name},
        {"$set": {"age": student.age}}
    )

    if result.matched_count == 1:
        return students_collection.find_one(
            {"name": name},
            {"_id": 0}
        )

    raise HTTPException(
        status_code=404,
        detail="student not found"
    )









@app.delete("/students/{name}")
def delete_student(name: str):

    result = students_collection.delete_one(
        {"name": name}
    )

    if result.deleted_count == 1:
        return {
            "message": "student deleted"
        }

    raise HTTPException(
        status_code=404,
        detail="student not found"
    )
