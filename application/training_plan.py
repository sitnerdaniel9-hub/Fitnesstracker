from repository.training_plan_repository import TrainingPlanRepository
from application.inputs.plan_exercise_input import PlanExerciseInput
from models.training_plan import TrainingPlan
from models.plan_exercise import PlanExercise
from sqlalchemy.orm import Session

#Erstellt aus einem PlanExerciseInput eine PlanExercise
def to_plan_exercise(exercise: PlanExerciseInput, index: int) -> PlanExercise:
    return PlanExercise(
        name=exercise.name,
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
def add_plan_exercise(session: Session, training_plan_id: int, exercise: PlanExerciseInput) -> TrainingPlan:
    repo = TrainingPlanRepository(session)
    try:
        training_plan = repo.find_by_id(training_plan_id)
        if training_plan is None:
            raise ValueError(f"training plan with id {training_plan_id} not found")
        plan_exercise = to_plan_exercise(exercise, len(training_plan.plan_exercises) + 1)
        training_plan.plan_exercises.append(plan_exercise)
        session.commit()
        return training_plan
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










    
    
