# python -m uvicorn main:app --reload

from fastapi import FastAPI

from database import Base, engine
from models.student import Student

from routers.students import router


Base.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(router)