from pydantic import BaseModel, Field


class Student(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    age: int = Field(ge=0, le=120)