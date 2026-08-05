from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from sqlalchemy.orm import Session

from api.schemas.workout import WorkoutRead, WorkoutCreate, WorkoutReadDetailed, WorkoutExerciseCreate, WorkoutSetCreate, WorkoutFinish, WorkoutSetCreateFromPlan
from application import workout
from application.inputs.workout_exercise_input import WorkoutExerciseInput
from application.inputs.workout_set_input import WorkoutSetInput
from db import get_db
from application.workout import (
    add_set_to_workout,
    create_workout,
    get_workout,
    get_workouts,
    get_workouts_by_name,
    get_workouts_by_date,
    find_workouts_by_training_plan,
    remove_workout,
    add_workout_exercise,
    add_workout_set,
    end_workout
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

@router.get("/{workout_id}", response_model=WorkoutReadDetailed)
def list_workout(workout_id: int, db: Session = Depends(get_db)):
    workout = get_workout(db, workout_id)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout

@router.post("", response_model=WorkoutRead, status_code=201)
def create_new_workout(payload: WorkoutCreate, db: Session = Depends(get_db)):
    return create_workout(db, payload.name, training_plan_id=payload.training_plan_id, started_at=payload.started_at)

@router.post("/{workout_id}/workout_exercises", response_model=WorkoutReadDetailed, status_code=201)
def create_workout_exercise(workout_id: int, payload: WorkoutExerciseCreate, db: Session = Depends(get_db)):
    return add_workout_exercise(db,
                                workout_id,
                                WorkoutExerciseInput(exercise_id=payload.exercise_id, plan_exercise_id=payload.plan_exercise_id, sets=[]))

@router.post("/{workout_id}/sets", response_model=WorkoutReadDetailed, status_code=201)
def create_workout_set(workout_id: int, payload: WorkoutSetCreateFromPlan, db: Session = Depends(get_db)):
    return add_set_to_workout(db, workout_id, payload.exercise_id, payload.plan_exercise_id, WorkoutSetInput(weight=payload.weight, reps=payload.reps, duration_time=payload.duration_time, is_warmup=payload.is_warmup))

@router.post("/{workout_id}/workout_exercises/{workout_exercise_id}/sets", response_model=WorkoutReadDetailed, status_code=201)
def add_set(workout_id: int, workout_exercise_id: int, payload: WorkoutSetCreate, db: Session = Depends(get_db)):
    return add_workout_set(db, workout_id, workout_exercise_id, WorkoutSetInput(weight=payload.weight, reps=payload.reps, duration_time=payload.duration_time, is_warmup=payload.is_warmup))

@router.delete("/{workout_id}", status_code=204)
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    remove_workout(db, workout_id)


@router.patch("/{workout_id}", response_model=WorkoutRead)
def finish_workout(workout_id: int, payload: WorkoutFinish, db: Session = Depends(get_db)):
    workout = end_workout(db, workout_id, payload.completed_at)
    return workout

