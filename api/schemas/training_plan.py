from pydantic import BaseModel
from datetime import datetime

class TrainingPlanRead(BaseModel):
    id: int
    name: str
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}