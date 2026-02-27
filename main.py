from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.training_plan import TrainingPlan
from models.plan_exercise import PlanExercise
from models.workout import Workout
from models.workout_exercise import WorkoutExercise
from models.workout_set import WorkoutSet
from repository.workout_repository import WorkoutRepository
from repository.training_plan_repository import TrainingPlanRepository
engine = create_engine("sqlite:///fitness_tracker.db", echo=True)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
repo = WorkoutRepository(session)
training_repo = TrainingPlanRepository(session)

workout = Workout(
    name="Push Day"
)

exercise1 = WorkoutExercise(
    name="Bench Press",
    order_index=1
)

exercise2 = WorkoutExercise(
    name="Incline Press",
    order_index=2
)

set1 = WorkoutSet(
    weight=60,
    reps=8
)

set2 = WorkoutSet(
    weight=80,
    reps=10
)
exercise1.sets.append(set1)
exercise2.sets.append(set2)
workout.workout_exercises.extend([exercise1, exercise2])

repo.create(workout)
session.commit()

loaded = repo.find_by_id(workout.id)

print("Workout geladen", loaded)
print("Exersices", loaded.workout_exercises[0].name)
print("Set1", loaded.workout_exercises[0].sets[0].reps)

repo.delete(workout)
session.commit()

plan = TrainingPlan(
    name="Push Plan",
    active=True
)

ex1 = PlanExercise(
    name="Bench Press",
    order_index=1,
    targeted_weight=80,
    min_targeted_reps=8,
    max_targeted_reps=10
)

ex2 = PlanExercise(
    name="Incline Press",
    order_index=2,
    targeted_weight=60,
    min_targeted_reps=10,
    max_targeted_reps=12
)

plan.plan_exercises.extend([ex1, ex2])

training_repo.create(plan)
session.commit()

loaded = training_repo.find_by_id(plan.id)

print("Plan:", loaded.name)
print("Exercise 1:", loaded.plan_exercises[0].name)
print("Order:", loaded.plan_exercises[0].order_index)

training_repo.delete(plan)
session.commit()
