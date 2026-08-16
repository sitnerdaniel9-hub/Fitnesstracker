from pydantic import BaseModel
from application.inputs.analysis_inputs import WeightData, RepData, TimeData

class ExerciseCreate(BaseModel):
    name: str


class ExerciseRead(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}

class WeightProgressionRead(BaseModel):
    weight_data: list[WeightData]
    avg_weight_gain: float | None

class ProgressionRead(BaseModel):
    rep_data: list[RepData]
    time_data: list[TimeData]
    avg_rep_gain: float | None
    avg_time_gain: float | None