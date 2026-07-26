from repository.workout_repository import WorkoutRepository
from repository.training_plan_repository import TrainingPlanRepository
from application.inputs.workout_set_input import WorkoutSetInput
from application.inputs.workout_exercise_input import WorkoutExerciseInput
from application.inputs.plan_exercise_input import PlanExerciseInput
from application.training_plan import create_training_plan
from datetime import datetime
from models.training_plan import TrainingPlan
from models.workout import Workout
from models.workout_exercise import WorkoutExercise
from models.plan_exercise import PlanExercise
from models.workout_set import WorkoutSet
from sqlalchemy.orm import Session

def to_workout_set(set: WorkoutSetInput) -> WorkoutSet:
    return WorkoutSet(
        weight = set.weight,
        reps = set.reps,
        duration_time = set.duration_time,
        isWarmup = set.is_warmup
    )

def validate_plan_exercise_logic(workout: Workout, plan_exercise_id: int| None) -> None:
    if plan_exercise_id is None:
        return

    if workout.training_plan_id is None:
        raise ValueError("plan_exercise_id is set, but workout has no training_plan_id")

    training_plan = workout.training_plan
    for plan_ex in training_plan.plan_exercises:
        if plan_ex.id == plan_exercise_id:
            return
    raise ValueError(f"plan_exercise {plan_exercise_id} does not belong to training_plan {training_plan.id} of workout {workout.id}")
    
def find_workout_exercise_for_workout_by_id(workout: Workout, workout_exercise_id: int) -> WorkoutExercise | None:
    for ex in workout.workout_exercises:
        if ex.id == workout_exercise_id:
            return ex
    
    return None

def find_set_for_workout_exercise_by_id(workout_exercise: WorkoutExercise, workout_set_id: int) -> WorkoutSet | None:
    for w_set in workout_exercise.sets:
        if w_set.id == workout_set_id:
            return w_set
    return None

#Erstellt ein frisches Workout ohne Übungen
def create_workout(session: Session, name: str, training_plan_id: int | None, started_at: datetime | None) -> Workout:
    if not name or not name.strip():
        raise ValueError("name must not be empty")
    temp : datetime
    if started_at is None:
        temp = datetime.now()
    else:
        temp = started_at
    workout_repo = WorkoutRepository(session)
    training_repo = TrainingPlanRepository(session)
    workout = Workout(
        name = name, 
        started_at = temp,
    )
    try:
        if training_plan_id is not None:
            training_plan = training_repo.find_by_id(training_plan_id)
            if training_plan is None:
                raise ValueError(f"training plan with id {training_plan_id} not found")
            workout.training_plan = training_plan
        workout = workout_repo.create(workout)
        session.commit()
        return workout
    except Exception:
        session.rollback()
        raise

#Ruft ein Workout ab
def get_workout(session: Session, workout_id: int) -> Workout:
    repo = WorkoutRepository(session)
    workout = repo.find_by_id(workout_id)
    if workout is None:
        raise ValueError(f"workout with id {workout_id} not found")
    return workout

#Liefert alle Workouts
def get_workouts(session: Session) -> list[Workout]:
    repo = WorkoutRepository(session)
    return repo.find_all()

#Liefert alle Workouts, die zu einem bestimmten Trainingsplan gehören
def find_workouts_by_training_plan(session: Session, training_plan_id: int) -> list[Workout]:
    repo = WorkoutRepository(session)
    return repo.find_by_training_plan_id(training_plan_id)

#Liefert alle Workouts, die einen bestimmten Suchstring enthalten
def get_workouts_by_name(session: Session, search: str) -> list[Workout]:
    repo = WorkoutRepository(session)
    return repo.find_by_name(search)

#Liefert alle Workouts, die nach einem bestimmten Zeitraum gestartet wurden
def get_workouts_by_date(session: Session, start : datetime, end: datetime) -> list[Workout]:
    repo = WorkoutRepository(session)
    return repo.find_by_date(start, end)

#Löscht ein Workout
def remove_workout(session: Session, workout_id: int) -> None:
    repo = WorkoutRepository(session)
    try:
        workout = repo.find_by_id(workout_id)
        if workout is None:
            raise ValueError(f"workout with id {workout_id} not found")
        repo.delete(workout)
        session.commit()
    except Exception:
        session.rollback()
        raise

#Löscht alle Workouts nach, die in einem bestimmten Zeitraum durchgeführt wurden.
def remove_workouts_by_date(session: Session, start : datetime, end: datetime) -> None:
    repo = WorkoutRepository(session)
    try:
        workouts = repo.find_by_date(start, end)
        for workout in workouts:
            repo.delete(workout)
        session.commit()
    except Exception:
        session.rollback()
        raise

#Fügt eine WorkoutExercise zu einem Workout hinzu

def add_workout_exercise(session: Session, workout_id: int, workout_exercise: WorkoutExerciseInput) -> Workout:
    repo = WorkoutRepository(session)
    try:
        workout = repo.find_by_id(workout_id)
        if workout is None:
            raise ValueError(f"workout with id {workout_id} not found")
        validate_plan_exercise_logic(workout, workout_exercise.plan_exercise_id)
        new_sets : list[WorkoutSet] = []
        for workout_set in workout_exercise.sets:
            new_sets.append(to_workout_set(workout_set))
        new_workout_exercise = WorkoutExercise(
            exercise_id = workout_exercise.exercise_id,
            plan_exercise_id = workout_exercise.plan_exercise_id,
            sets = new_sets,
        )
        workout.workout_exercises.append(new_workout_exercise)
        session.commit()
        return workout
    except Exception:
        session.rollback()
        raise

#Verändert eine WorkoutExercise in einem Workout

def update_workout_exercise(session: Session, workout_id: int, workout_exercise_id: int, workout_exercise_input: WorkoutExerciseInput) -> Workout:
    repo = WorkoutRepository(session)
    try:
        workout = repo.find_by_id(workout_id)
        if workout is None:
            raise ValueError(f"workout with id {workout_id} not found")
        validate_plan_exercise_logic(workout, workout_exercise_input.plan_exercise_id)
        workout_exercise = find_workout_exercise_for_workout_by_id(workout, workout_exercise_id)
        if workout_exercise is None:
            raise ValueError(f"WorkoutExercise with id {workout_exercise_id} not found")
        workout_exercise.exercise_id = workout_exercise_input.exercise_id
        workout_exercise.plan_exercise_id = workout_exercise_input.plan_exercise_id
        new_sets : list[WorkoutSet] = []
        for workout_set in workout_exercise_input.sets:
            new_sets.append(to_workout_set(workout_set))
        workout_exercise.sets = new_sets
        session.commit()
        return workout
    except Exception:
        session.rollback()
        raise

#Löscht eine WorkoutExercise aus einem Workout

def remove_workout_exercise(session: Session, workout_id: int, workout_exercise_id: int) -> Workout:
    repo = WorkoutRepository(session)
    try:
        workout = repo.find_by_id(workout_id)
        if workout is None:
            raise ValueError(f"workout with id {workout_id} not found")
        workout_exercise = find_workout_exercise_for_workout_by_id(workout, workout_exercise_id)
        if workout_exercise is None:
            raise ValueError(f"WorkoutExercise with id {workout_exercise_id} not found")
        workout.workout_exercises.remove(workout_exercise)
        session.commit()
        return workout
    except Exception:
        session.rollback()
        raise


#Fügt einer WorkoutExercise in einem Workout einen Satz hinzu

def add_workout_set(session: Session, workout_id: int, workout_exercise_id: int, workout_set_input: WorkoutSetInput) -> Workout:
    repo = WorkoutRepository(session)
    try:
        workout = repo.find_by_id(workout_id)
        if workout is None:
            raise ValueError(f"workout with id {workout_id} not found")
        workout_exercise = find_workout_exercise_for_workout_by_id(workout, workout_exercise_id)
        if workout_exercise is None:
            raise ValueError(f"WorkoutExercise with id {workout_exercise_id} not found")
        workout_set = to_workout_set(workout_set_input)
        workout_exercise.sets.append(workout_set)
        session.commit()
        return workout
    except Exception:
        session.rollback()
        raise

#Verändert einen Satz in einer WorkoutExercise in einem Workout

def update_workout_set(session: Session, workout_id: int, workout_exercise_id: int, workout_set_id: int, workout_set_input: WorkoutSetInput) -> Workout:
    repo = WorkoutRepository(session)
    try:
        workout = repo.find_by_id(workout_id)
        if workout is None:
            raise ValueError(f"workout with id {workout_id} not found")
        workout_exercise = find_workout_exercise_for_workout_by_id(workout, workout_exercise_id)
        if workout_exercise is None:
            raise ValueError(f"WorkoutExercise with id {workout_exercise_id} not found")
        workout_set = find_set_for_workout_exercise_by_id(workout_exercise, workout_set_id)
        if workout_set is None:
            raise ValueError(f"WorkoutSet with id {workout_set_id} not found")
        workout_set.weight = workout_set_input.weight
        workout_set.reps = workout_set_input.reps
        workout_set.duration_time = workout_set_input.duration_time
        workout_set.isWarmup = workout_set_input.is_warmup
        session.commit()
        return workout
    except Exception:
        session.rollback()
        raise

#Löscht einen Satz aus einer WorkoutExercise in einem Workout

def remove_workout_set(session: Session, workout_id: int, workout_exercise_id: int, workout_set_id: int) -> Workout:
    repo = WorkoutRepository(session)
    try:
        workout = repo.find_by_id(workout_id)
        if workout is None:
            raise ValueError(f"workout with id {workout_id} not found")
        workout_exercise = find_workout_exercise_for_workout_by_id(workout, workout_exercise_id)
        if workout_exercise is None:
            raise ValueError(f"WorkoutExercise with id {workout_exercise_id} not found")
        workout_set = find_set_for_workout_exercise_by_id(workout_exercise, workout_set_id)
        if workout_set is None:
            raise ValueError(f"WorkoutSet with id {workout_set_id} not found")
        workout_exercise.sets.remove(workout_set)
        session.commit()
        return workout
    except Exception:
        session.rollback()
        raise

#Schließt ein laufendes Workout ab
def end_workout(session: Session, workout_id: int) -> Workout:
    repo = WorkoutRepository(session)
    try:
        workout = repo.find_by_id(workout_id)
        if workout is None:
            raise ValueError(f"workout with id {workout_id} not found")
        workout.completed_at = datetime.now()
        session.commit()
        return workout
    except Exception:
        session.rollback()
        raise

#Erstellt aus einer Liste von WorkoutExercises eine liste von PlanExerciseInputs
def convert_workout_exercises_into_plan_exercises(workout_exercises: list[WorkoutExercise]) -> list[PlanExerciseInput]:
    plan_exercises : list[PlanExerciseInput] = []
    
    for ex in workout_exercises:
        set_ref_list : list[WorkoutSet] = []
        for w_set in ex.sets:
            if not w_set.isWarmup:
                set_ref_list.append(w_set)
        if not set_ref_list:
            raise ValueError(f"No Sets for {ex.exercise.name} found that are not warmup sets")
        #es wird einfach immer der erste Arbeitssatz als Referenz genommen
        reference_set = set_ref_list[0]
        plan_exercise_input = PlanExerciseInput(
            exercise_id=ex.exercise_id,
            targeted_weight= reference_set.weight,
            min_targeted_reps=reference_set.reps,
            max_targeted_reps=reference_set.reps,
            min_duration_time=reference_set.duration_time,
            max_duration_time=reference_set.duration_time,
            rest_sec=None
        )
        plan_exercises.append(plan_exercise_input)
    return plan_exercises


#Speichert ein Workout als Trainingsplan
def save_as_training_plan(session: Session, workout_id: int) -> TrainingPlan:
    repo = WorkoutRepository(session)

    workout = repo.find_by_id(workout_id)
    if workout is None:
        raise ValueError(f"workout with id {workout_id} not found")
    plan_exercises = convert_workout_exercises_into_plan_exercises(workout.workout_exercises)
    return create_training_plan(session, workout.name, plan_exercises)



    


