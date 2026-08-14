from pydantic import BaseModel
from datetime import datetime
from api.schemas.exercise import ExerciseRead

class TrainingPlanRead(BaseModel):
    id: int
    name: str
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}

class PlanExerciseRead(BaseModel):
    id: int
    training_plan_id: int
    exercise: ExerciseRead
    targeted_weight: float | None
    min_targeted_reps: int | None
    max_targeted_reps: int | None
    min_targeted_duration_time: float | None
    max_targeted_duration_time: float | None
    break_time: float | None

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}

class TrainingPlanCreateOrUpdate(BaseModel):
    name: str

class PlanExerciseUpdateOrCreate(BaseModel):
    exercise_id: int
    targeted_weight: float | None
    min_targeted_reps: int | None
    max_targeted_reps: int | None
    min_duration_time: float | None
    max_duration_time: float | None
    rest_sec: float | None