import datetime

from pydantic import BaseModel

class WorkoutRead(BaseModel):
    id: int
    name: str
    started_at: datetime
    completed_at: datetime
    training_plan_id: int | None

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}