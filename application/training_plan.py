from repository.training_plan_repository import TrainingPlanRepository
from application.inputs.plan_exercise_input import PlanExerciseInput
from models.training_plan import TrainingPlan
from models.plan_exercise import PlanExercise
from sqlalchemy.orm import Session

#Erstellt aus einem PlanExerciseInput eine PlanExercise
def to_plan_exercise(exercise: PlanExerciseInput, index: int) -> PlanExercise:
    return PlanExercise(
        exercise_id = exercise.exercise_id,
        order_index = index,
        targeted_weight = exercise.targeted_weight,
        min_targeted_reps = exercise.min_targeted_reps,
        max_targeted_reps = exercise.max_targeted_reps,
        min_targeted_duration_time = exercise.min_duration_time,
        max_targeted_duration_time=exercise.max_duration_time,
        break_time=exercise.rest_sec,
    )

def find_plan_exercise_by_id(exercises: list[PlanExercise], plan_exercise_id: int) -> PlanExercise | None:
    for ex in exercises:
        if plan_exercise_id == ex.id:
            return ex
    
    return None

#Sorgt dafür, dass die order_indexe in den Übungen wieder lückenslos sind
def normalize_plan_exercise_order(training_plan: TrainingPlan) -> None:
    for index, exercise in enumerate(training_plan.plan_exercises, start=1):
        exercise.order_index = index
    
#Erstellt einen neuen Trainingsplan
def create_training_plan(session: Session, plan_name: str, exercises: list[PlanExerciseInput]) -> TrainingPlan:
    if not plan_name or not plan_name.strip():
        raise ValueError("name must not be empty")

    repo = TrainingPlanRepository(session)
    training_plan = TrainingPlan(name=plan_name)

    for index, ex in enumerate(exercises, start=1):
        plan_exercise = to_plan_exercise(ex, index)
        training_plan.plan_exercises.append(plan_exercise)

    try:
        training_plan = repo.create(training_plan)
        session.commit()
        return training_plan
    except Exception:
        session.rollback()
        raise

#Fügt einen PlanExercise am Ende eines Trainingsplans ein.
def add_plan_exercise(session: Session, training_plan_id: int, exercise: PlanExerciseInput) -> PlanExercise:
    repo = TrainingPlanRepository(session)
    try:
        training_plan = repo.find_by_id(training_plan_id)
        if training_plan is None:
            raise ValueError(f"training plan with id {training_plan_id} not found")
        plan_exercise = to_plan_exercise(exercise, len(training_plan.plan_exercises) + 1)
        training_plan.plan_exercises.append(plan_exercise)
        session.commit()
        return plan_exercise
    except Exception:
        session.rollback()
        raise

#Entfernt eine PlanExersice aus einem Trainingsplan
def remove_plan_exercise(session: Session, training_plan_id: int, plan_exercise_id: int) -> TrainingPlan:
    repo = TrainingPlanRepository(session)
    try:
        training_plan = repo.find_by_id(training_plan_id)
        if training_plan is None:
            raise ValueError(f"training plan with id {training_plan_id} not found")
        ex = find_plan_exercise_by_id(training_plan.plan_exercises, plan_exercise_id)
        if ex is None:
            raise ValueError(f"PlanExercise with id {plan_exercise_id} not found")
        
        training_plan.plan_exercises.remove(ex)
        normalize_plan_exercise_order(training_plan)
        session.commit()
        return training_plan
    except Exception:
        session.rollback()
        raise

#Gibt den Trainingsplan mit der übergebenen id zurück.
def find_training_plan_by_id(session: Session, training_plan_id: int) -> TrainingPlan:
    repo = TrainingPlanRepository(session)
    training_plan = repo.find_by_id(training_plan_id)
    if training_plan is None:
        raise ValueError(f"training plan with id {training_plan_id} not found")
    return training_plan


#Gibt alle Trainingspläne zurück
def get_all_training_plans(session: Session) -> list[TrainingPlan]:
    repo = TrainingPlanRepository(session)
    return repo.find_all()

#Aktualisiert eine PlanExercise in einem Trainingsplan
def update_plan_exercise(session: Session, training_plan_id: int, plan_exercise_id: int, plan_exercise_input: PlanExerciseInput) -> PlanExercise:
    repo = TrainingPlanRepository(session)
    try:
        training_plan = repo.find_by_id(training_plan_id)
        if training_plan is None:
            raise ValueError(f"training plan with id {training_plan_id} not found")
        ex = find_plan_exercise_by_id(training_plan.plan_exercises, plan_exercise_id)
        if ex is None:
            raise ValueError(f"PlanExercise with id {plan_exercise_id} not found")
        
        ex.exercise_id = plan_exercise_input.exercise_id
        ex.targeted_weight = plan_exercise_input.targeted_weight
        ex.min_targeted_reps = plan_exercise_input.min_targeted_reps
        ex.max_targeted_reps = plan_exercise_input.max_targeted_reps
        ex.min_targeted_duration_time = plan_exercise_input.min_duration_time
        ex.max_targeted_duration_time = plan_exercise_input.max_duration_time
        ex.break_time = plan_exercise_input.rest_sec

        session.commit()
        return ex
    except Exception:
        session.rollback()
        raise

#Bennent einen Trainingsplan um
def rename_training_plan(session: Session, training_plan_id: int, new_name: str) -> TrainingPlan:
    repo = TrainingPlanRepository(session)
    try:
        training_plan = repo.find_by_id(training_plan_id)
        if training_plan is None:
            raise ValueError(f"training plan with id {training_plan_id} not found")
        training_plan.name = new_name
        session.commit()
        return training_plan
    except Exception:
        session.rollback()
        raise

#Setzt den Status eines Trainingsplans
def toggle_training_plan_status(session: Session, training_plan_id : int) -> TrainingPlan:
    repo = TrainingPlanRepository(session)
    try:
        training_plan = repo.find_by_id(training_plan_id)
        if training_plan is None:
            raise ValueError(f"training plan with id {training_plan_id} not found")
        training_plan.active = not training_plan.active
        session.commit()
        return training_plan
    except Exception:
        session.rollback()
        raise

#ändert die Reihenfolge einer PlanExercise in einem Trainingsplan
def reorder_plan_exercise(session: Session, training_plan_id: int, plan_exercise_id: int, new_position: int) -> TrainingPlan:
    repo = TrainingPlanRepository(session)
    try:
        training_plan = repo.find_by_id(training_plan_id)
        if training_plan is None:
            raise ValueError(f"training plan with id {training_plan_id} not found")
        if len(training_plan.plan_exercises) < new_position or new_position < 1:
            raise ValueError(f"new_position has to be smaller then or equal to the biggest order_index an 1.")
        ex = find_plan_exercise_by_id(training_plan.plan_exercises, plan_exercise_id)
        if ex is None:
            raise ValueError(f"PlanExercise with id {plan_exercise_id} not found")
        training_plan.plan_exercises.remove(ex)
        training_plan.plan_exercises.insert(new_position - 1, ex)
        normalize_plan_exercise_order(training_plan)
        session.commit()
        return training_plan
    except Exception:
        session.rollback()
        raise

#Findet alle Trainingspläne, die den Suchstring enthalten. Case Insensitive
def find_training_plans_by_name(session: Session, search: str) -> list[TrainingPlan]:
    repo = TrainingPlanRepository(session)
    return repo.find_by_name(search)

#Löscht einen Trainingsplan
def remove_training_plan(session: Session, id: int) -> None:
    repo = TrainingPlanRepository(session)
    try:
        training_plan = repo.find_by_id(id)
        if training_plan is None:
            raise ValueError(f"training_plan with id {id} not found")
        repo.delete(training_plan)
        session.commit()
    except Exception:
        session.rollback()
        raise







    
    
