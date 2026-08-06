from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from sqlalchemy.orm import Session

from api.schemas.training_plan import TrainingPlanRead, PlanExerciseRead, TrainingPlanCreate
from db import get_db
from application.training_plan import (
    find_plan_exercise_by_id,
    get_all_training_plans,
    find_training_plan_by_id,
    find_training_plans_by_name,
    create_training_plan,
    toggle_training_plan_status,
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

@router.get("/{training_plan_id}/plan_exercises", response_model=list[PlanExerciseRead])
def get_plan_exercises(training_plan_id: int, db: Session = Depends(get_db)):
    try:
        training_plan = find_training_plan_by_id(db, training_plan_id)
        return training_plan.plan_exercises
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{training_plan_id}/plan_exercises/{plan_exercise_id}", response_model=PlanExerciseRead)
def get_plan_exercise(training_plan_id: int, plan_exercise_id: int, db: Session = Depends(get_db)):
    try:
        training_plan = find_training_plan_by_id(db, training_plan_id)
        plan_exercise = find_plan_exercise_by_id(training_plan.plan_exercises, plan_exercise_id)
        if plan_exercise is None:
            raise ValueError(f"PlanExercise with id {plan_exercise_id} not found")
        return plan_exercise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("", response_model = TrainingPlanRead)
def add_training_plan(payload: TrainingPlanCreate, db: Session = Depends(get_db)):
    return create_training_plan(db, payload.name, [])

@router.patch("/{training_plan_id}", response_model=TrainingPlanRead)
def switch_active_status(training_plan_id: int, db: Session = Depends(get_db)):
    return toggle_training_plan_status(db, training_plan_id)