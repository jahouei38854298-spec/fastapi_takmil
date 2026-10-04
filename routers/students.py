from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy import select
from models.student import Student as StudentModel
from schemas.student import Student
from services.student_service import (
    students,
    find_student_by_name,
    add_student,
    update_student as update_student_service,
    delete_student as delete_student_service
)
router = APIRouter()



@router.get("/db-students")
def get_db_students(db: Session = Depends(get_db)):

    result = db.execute(
        select(StudentModel)
    )

    students = result.scalars().all()

    return students




@router.post("/db-students")
def create_db_student(
    student: Student,
    db: Session = Depends(get_db)
):

    new_student = StudentModel(
        name=student.name,
        age=student.age
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return {
    "id": new_student.id,
    "name": new_student.name,
    "age": new_student.age
    }



@router.get("/db-test")
def db_test(db: Session = Depends(get_db)):
    return {
        "message": "database connected"
    }



@router.get("/students")
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



@router.get("/students/{name}")
def get_student(name: str):

    student = find_student_by_name(name)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="student not found"
        )

    return student



@router.post("/students")
def create_student(student: Student):

    existing_student = find_student_by_name(student.name)

    if existing_student is not None:
        raise HTTPException(
            status_code=400,
            detail="student already exists"
        )

    return add_student(student)




@router.put("/students/{name}")
def update_student(name: str, student: Student):

    updated_student = update_student_service(name, student)

    if updated_student is None:
        raise HTTPException(
            status_code=404,
            detail="student not found"
        )

    return updated_student


@router.delete("/students/{name}")
def delete_student(name: str):

    deleted = delete_student_service(name)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="student not found"
        )

    return {
        "message": "student deleted"
    }

