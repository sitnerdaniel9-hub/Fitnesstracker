from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base
from models.training_plan import TrainingPlan
from models.plan_exercise import PlanExercise
from models.workout import Workout
from models.workout_exercise import WorkoutExercise
from models.workout_set import WorkoutSet

engine = create_engine("sqlite:///fitness_tracker.db", echo=True)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# -------------------------
# 1. Trainingsplan erstellen
# -------------------------

plan = TrainingPlan(name="Upper Body")

plan.plan_exercises = [
    PlanExercise(
        name="Bench Press",
        order_index=1,
        targeted_weight=80,
        min_targeted_reps=8,
        max_targeted_reps=12,
        min_targeted_duration_time=None,
        max_targeted_duration_time=None,
        break_time=90
    ),
    PlanExercise(
        name="Pull Ups",
        order_index=2,
        targeted_weight=None,
        min_targeted_reps=6,
        max_targeted_reps=10,
        min_targeted_duration_time=None,
        max_targeted_duration_time=None,
        break_time=120
    )
]

session.add(plan)
session.commit()

# -------------------------
# 2. Workout erstellen
# -------------------------

workout = Workout(
    name="Upper Body Session",
    training_plan=plan
)

workout.workout_exercises = [
    WorkoutExercise(
        name="Bench Press",
        order_index=1,
        plan_exercise=plan.plan_exercises[0],
        sets=[
            WorkoutSet(weight=80, reps=10),
            WorkoutSet(weight=80, reps=9),
            WorkoutSet(weight=75, reps=10),
        ]
    ),
    WorkoutExercise(
        name="Pull Ups",
        order_index=2,
        plan_exercise=plan.plan_exercises[1],
        sets=[
            WorkoutSet(reps=8),
            WorkoutSet(reps=7),
            WorkoutSet(reps=6),
        ]
    )
]

session.add(workout)
session.commit()

# -------------------------
# 3. Daten prüfen
# -------------------------

workouts = session.query(Workout).all()

for w in workouts:
    print(f"\nWorkout: {w.name}")
    for ex in w.workout_exercises:
        print(f"  Exercise: {ex.name}")
        for s in ex.sets:
            print(f"    Set -> weight={s.weight}, reps={s.reps}, duration={s.duration_time}, warmup={s.isWarmup}")