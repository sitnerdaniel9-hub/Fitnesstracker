from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.schemas.exercise import ExerciseCreate, ExerciseRead, WeightProgressionRead, ProgressionRead
from api.schemas.workout import WorkoutSetRead
from datetime import datetime

from db import get_db
from application.exercise import (
    find_exercise_by_id,
    find_exercise_by_name,
    create_exercise,
    find_all_exercises,
)

from application.workout import (
    get_best_weight_per_workout_by_exercise_id,
    get_best_reps_per_workout_by_exercise_id,
    get_best_time_per_workout_by_exercise_id
)

from application.analysis import (
    get_pr_for_exercise,
    get_avg_weight_gain,
    get_avg_rep_increase,
    get_avg_time_increase,
)

router = APIRouter(prefix="/api/exercises", tags=["exercises"])

@router.get("", response_model=list[ExerciseRead])
def list_exercises(name: str | None = None, db: Session = Depends(get_db)):
    if name is not None:
        exercise = find_exercise_by_name(db, name)
        return [exercise] if exercise else []
    return find_all_exercises(db)

@router.get("/{exercise_id}", response_model=ExerciseRead)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    exercise = find_exercise_by_id(db, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise

@router.get("/{exercise_id}/analysis/pr", response_model=WorkoutSetRead | None)
def get_pr(exercise_id: int, db: Session = Depends(get_db)):
    return get_pr_for_exercise(db, exercise_id)

@router.get("/{exercise_id}/analysis/progression", response_model=WeightProgressionRead)
def get_weight_gain(exercise_id: int, start: datetime | None = None, end: datetime | None = None, db: Session = Depends(get_db)):
    weight_data = get_best_weight_per_workout_by_exercise_id(db, exercise_id, start, end)
    avg_weight_gain = get_avg_weight_gain(weight_data)
    return WeightProgressionRead(
        weight_data=weight_data,
        avg_weight_gain=avg_weight_gain,
    )

@router.get("/{exercise_id}/analysis/progression/weight", response_model=ProgressionRead)
def get_progression_for_weight(exercise_id: int, weight: float | None = None, db: Session = Depends(get_db)):
    rep_data = get_best_reps_per_workout_by_exercise_id(db, exercise_id, weight)
    time_data = get_best_time_per_workout_by_exercise_id(db, exercise_id, weight)
    avg_rep_gain = get_avg_rep_increase(rep_data)
    avg_time_gain = get_avg_time_increase(time_data)
    return ProgressionRead(
        rep_data=rep_data,
        time_data=time_data,
        avg_rep_gain=avg_rep_gain,
        avg_time_gain=avg_time_gain
    )

@router.post("", response_model=ExerciseRead, status_code=201)
def create_new_exercise(payload: ExerciseCreate, db: Session = Depends(get_db)):
    return create_exercise(db, payload.name)