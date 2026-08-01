from pydantic import BaseModel
from datetime import datetime

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
    exercise_id: int
    targeted_weight: float | None
    min_targeted_reps: int | None
    max_targeted_reps: int | None
    min_targeted_duration_time: float | None
    max_targeted_duration_time: float | None
    break_time: float | None

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}