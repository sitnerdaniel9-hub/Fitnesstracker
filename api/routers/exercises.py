from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.schemas.exercise import ExerciseCreate, ExerciseRead

from db import get_db
from application.exercise import (
    find_exercise_by_id,
    find_exercise_by_name,
    create_exercise,
    find_all_exercises,
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

@router.post("", response_model=ExerciseRead, status_code=201)
def create_new_exercise(payload: ExerciseCreate, db: Session = Depends(get_db)):
    return create_exercise(db, payload.name)