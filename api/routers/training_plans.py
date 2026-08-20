from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.schemas.training_plan import TrainingPlanRead, PlanExerciseRead, TrainingPlanCreateOrUpdate, PlanExerciseUpdateOrCreate, PlanExerciseReorder
from db import get_db
from application.training_plan import (
    find_plan_exercise_by_id,
    get_all_training_plans,
    find_training_plan_by_id,
    find_training_plans_by_name,
    create_training_plan,
    toggle_training_plan_status,
    update_plan_exercise,
    add_plan_exercise,
    remove_training_plan,
    remove_plan_exercise,
    rename_training_plan,
    reorder_plan_exercise
)

from application.workout import (
    save_as_training_plan
)

from application.inputs.plan_exercise_input import PlanExerciseInput

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

@router.post("", response_model = TrainingPlanRead, status_code=201)
def add_training_plan(payload: TrainingPlanCreateOrUpdate, db: Session = Depends(get_db)):
    return create_training_plan(db, payload.name, [])

@router.post("/from_workout", response_model=TrainingPlanRead, status_code=201)
def save_workout_as_training_plan(workout_id: int, db: Session = Depends(get_db)):
    return save_as_training_plan(db, workout_id)

@router.post("/{training_plan_id}/plan_exercises", response_model=PlanExerciseRead)
def create_plan_exercise(training_plan_id: int, payload: PlanExerciseInput, db: Session = Depends(get_db)):
    try:
        return add_plan_exercise(db, training_plan_id, PlanExerciseInput(
            exercise_id=payload.exercise_id,
            targeted_weight=payload.targeted_weight,
            min_targeted_reps=payload.min_targeted_reps,
            max_targeted_reps=payload.max_targeted_reps,
            min_duration_time=payload.min_duration_time,
            max_duration_time=payload.max_duration_time,
            rest_sec=payload.rest_sec
        ))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{training_plan_id}", response_model=TrainingPlanRead)
def switch_active_status(training_plan_id: int, db: Session = Depends(get_db)):
    return toggle_training_plan_status(db, training_plan_id)

@router.patch("/{training_plan_id}/rename", response_model=TrainingPlanRead)
def edit_training_plan_name(training_plan_id: int, payload: TrainingPlanCreateOrUpdate, db: Session = Depends(get_db)):
    return rename_training_plan(db, training_plan_id, payload.name)

@router.patch("/{training_plan_id}/plan_exercises/{plan_exercise_id}", response_model=PlanExerciseRead)
def edit_plan_exercise(training_plan_id: int, plan_exercise_id: int, payload: PlanExerciseUpdateOrCreate, db: Session = Depends(get_db)):
    try:
        return update_plan_exercise(db, training_plan_id, plan_exercise_id, PlanExerciseInput(
            exercise_id=payload.exercise_id,
            targeted_weight=payload.targeted_weight,
            min_targeted_reps=payload.min_targeted_reps,
            max_targeted_reps=payload.max_targeted_reps,
            min_duration_time=payload.min_duration_time,
            max_duration_time=payload.max_duration_time,
            rest_sec=payload.rest_sec
        ))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{training_plan_id}/plan_exercises/{plan_exercise_id}/reorder", response_model=PlanExerciseRead)
def edit_plan_exercise_order(training_plan_id: int, plan_exercise_id: int, payload: PlanExerciseReorder, db: Session = Depends(get_db)):
    try:
        training_plan = reorder_plan_exercise(db, training_plan_id, plan_exercise_id, payload.new_position)
        return find_plan_exercise_by_id(training_plan.plan_exercises, plan_exercise_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("", status_code=204)
def delete_training_plans(ids: list[int], db: Session = Depends(get_db)):
    for id in ids:
        try:
            remove_training_plan(db, id)
        except ValueError:
            continue

@router.delete("/{training_plan_id}/plan_exercises", status_code=204)
def delete_plan_exercises(training_plan_id: int, ids: list[int], db: Session = Depends(get_db)):
    for id in ids:
        try:
            remove_plan_exercise(db, training_plan_id, id)
        except ValueError:
            continue