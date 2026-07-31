from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from sqlalchemy.orm import Session

from api.schemas.training_plan import TrainingPlanRead
from db import get_db
from application.training_plan import (
    get_all_training_plans,
    find_training_plan_by_id,
    find_training_plans_by_name
)

router = APIRouter(prefix="/api/training_plans", tags=["training_plans"])

@router.get("", response_model=list[TrainingPlanRead])
def list_training_plans(name: str | None = None, db: Session = Depends(get_db)):
    if name is not None:
        return find_training_plans_by_name(db, name)
    return get_all_training_plans(db)

@router.get("/{training_plan_id}", response_model=TrainingPlanRead)
def get_training_plan(training_plan_id: int, db: Session = Depends(get_db)):
    try:
        return find_training_plan_by_id(db, training_plan_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

