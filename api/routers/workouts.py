from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from sqlalchemy.orm import Session

from api.schemas.workout import WorkoutRead
from db import get_db
from application.workout import (
    get_workout,
    get_workouts,
    get_workouts_by_name,
    get_workouts_by_date,
    find_workouts_by_training_plan
)


router = APIRouter(prefix="/api/workouts", tags=["workouts"])

@router.get("", response_model=list[WorkoutRead])
def list_workouts(name: str | None = None,
    start: datetime | None = None, 
    end: datetime | None = None,
    training_plan_id: int | None = None,
    db: Session = Depends(get_db)):
    date_filter_used = start is not None or end is not None
    active = sum([name is not None, date_filter_used, training_plan_id is not None])

    if active > 1:
        raise HTTPException(400, "Only one filter can be used at a time. Please use either 'name', 'start' and 'end' together, or 'training_plan_id'.")
    
    if name is not None:
        return get_workouts_by_name(db, name)
    if start is not None and end is not None:
        return get_workouts_by_date(db, start, end)
    if training_plan_id is not None:
        return find_workouts_by_training_plan(db, training_plan_id)
    return get_workouts(db)

@router.get("/{workout_id}", response_model=WorkoutRead)
def list_workout(workout_id: int, db: Session = Depends(get_db)):
    workout = get_workout(db, workout_id)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout

