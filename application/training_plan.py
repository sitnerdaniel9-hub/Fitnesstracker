from repository.training_plan_repository import TrainingPlanRepository
from application.inputs.plan_exercise_input import PlanExerciseInput
from models.training_plan import TrainingPlan
from models.plan_exercise import PlanExercise
from sqlalchemy.orm import Session

def create_training_plan(session: Session, plan_name: str, exercises: list[PlanExerciseInput]) -> TrainingPlan:
    if not plan_name or not plan_name.strip():
        raise ValueError("name must not be empty")

    repo = TrainingPlanRepository(session)
    training_plan = TrainingPlan(name=plan_name)

    for index, ex in enumerate(exercises, start=1):
        plan_exercise = PlanExercise(
            name=ex.name,
            order_index=index,
            targeted_weight=ex.targeted_weight,
            min_targeted_reps=ex.min_targeted_reps,
            max_targeted_reps=ex.max_targeted_reps,
            min_targeted_duration_time=ex.min_duration_time,
            max_targeted_duration_time=ex.max_duration_time,
            break_time=ex.rest_sec,
            training_plan=training_plan,
        )
        training_plan.plan_exercises.append(plan_exercise)

    try:
        training_plan = repo.create(training_plan)
        session.commit()
        return training_plan
    except Exception:
        session.rollback()
        raise



    
    
