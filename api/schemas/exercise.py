from pydantic import BaseModel

class ExerciseCreate(BaseModel):
    name: str


class ExerciseRead(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}