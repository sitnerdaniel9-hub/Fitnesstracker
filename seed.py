from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base
from application.exercise import create_exercise
from application.training_plan import create_training_plan, add_plan_exercise
from application.workout import create_workout, add_workout_exercise
from application.inputs.plan_exercise_input import PlanExerciseInput
from application.inputs.workout_exercise_input import WorkoutExerciseInput
from application.inputs.workout_set_input import WorkoutSetInput

engine = create_engine("sqlite:///fitness_tracker.db")
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()


def seed():
    kniebeuge = create_exercise(session, "Kniebeuge (Test)")
    kreuzheben = create_exercise(session, "Kreuzheben (Test)")
    klimmzug = create_exercise(session, "Klimmzug (Test)")
    bizepscurl = create_exercise(session, "Bizepscurl (Test)")
    plank = create_exercise(session, "Plank (Test)")

    plan = create_training_plan(
        session,
        "Testplan Ganzkörper",
        [
            PlanExerciseInput(
                exercise_id=kniebeuge.id,
                targeted_weight=80.0,
                min_targeted_reps=6,
                max_targeted_reps=10,
                min_duration_time=None,
                max_duration_time=None,
                rest_sec=120.0,
            ),
            PlanExerciseInput(
                exercise_id=kreuzheben.id,
                targeted_weight=100.0,
                min_targeted_reps=5,
                max_targeted_reps=8,
                min_duration_time=None,
                max_duration_time=None,
                rest_sec=150.0,
            ),
        ],
    )
    kniebeuge_pe = plan.plan_exercises[0]
    kreuzheben_pe = plan.plan_exercises[1]

    plan = add_plan_exercise(
        session,
        plan.id,
        PlanExerciseInput(
            exercise_id=plank.id,
            targeted_weight=None,
            min_targeted_reps=None,
            max_targeted_reps=None,
            min_duration_time=30.0,
            max_duration_time=60.0,
            rest_sec=60.0,
        ),
    )
    plank_pe = plan.plan_exercises[2]

    # Vier abgeschlossene, plangebundene Workouts über vier Wochen mit steigenden Gewichten
    base = datetime.now() - timedelta(weeks=4)
    for week, (kb_weight, kh_weight) in enumerate([(80.0, 100.0), (82.5, 102.5), (85.0, 105.0), (87.5, 110.0)]):
        started = base + timedelta(weeks=week)
        w = create_workout(session, f"Ganzkörper #{week + 1}", training_plan_id=plan.id, started_at=started)

        add_workout_exercise(
            session,
            w.id,
            WorkoutExerciseInput(
                exercise_id=kniebeuge.id,
                plan_exercise_id=kniebeuge_pe.id,
                sets=[
                    WorkoutSetInput(weight=kb_weight - 20, reps=8, duration_time=None, is_warmup=True),
                    WorkoutSetInput(weight=kb_weight, reps=8, duration_time=None, is_warmup=False),
                    WorkoutSetInput(weight=kb_weight, reps=7, duration_time=None, is_warmup=False),
                ],
            ),
        )
        add_workout_exercise(
            session,
            w.id,
            WorkoutExerciseInput(
                exercise_id=kreuzheben.id,
                plan_exercise_id=kreuzheben_pe.id,
                sets=[
                    WorkoutSetInput(weight=kh_weight - 20, reps=5, duration_time=None, is_warmup=True),
                    WorkoutSetInput(weight=kh_weight, reps=6, duration_time=None, is_warmup=False),
                ],
            ),
        )
        add_workout_exercise(
            session,
            w.id,
            WorkoutExerciseInput(
                exercise_id=plank.id,
                plan_exercise_id=plank_pe.id,
                sets=[WorkoutSetInput(weight=None, reps=None, duration_time=30.0 + week * 10, is_warmup=False)],
            ),
        )

        w.completed_at = started + timedelta(hours=1)
        session.commit()

    # Ein laufendes (nicht abgeschlossenes) plangebundenes Workout
    running = create_workout(
        session,
        "Ganzkörper #5 (läuft)",
        training_plan_id=plan.id,
        started_at=datetime.now() - timedelta(minutes=20),
    )
    add_workout_exercise(
        session,
        running.id,
        WorkoutExerciseInput(
            exercise_id=kniebeuge.id,
            plan_exercise_id=kniebeuge_pe.id,
            sets=[WorkoutSetInput(weight=90.0, reps=6, duration_time=None, is_warmup=False)],
        ),
    )

    # Zwei plan-lose, abgeschlossene Workouts (Klimmzug + Bizepscurl)
    for i, (reps, weight) in enumerate([(6, None), (8, None)]):
        started = datetime.now() - timedelta(weeks=2 - i)
        w = create_workout(session, f"Freies Training #{i + 1}", training_plan_id=None, started_at=started)
        add_workout_exercise(
            session,
            w.id,
            WorkoutExerciseInput(
                exercise_id=klimmzug.id,
                plan_exercise_id=None,
                sets=[
                    WorkoutSetInput(weight=None, reps=reps, duration_time=None, is_warmup=False),
                    WorkoutSetInput(weight=None, reps=reps - 1, duration_time=None, is_warmup=False),
                ],
            ),
        )
        add_workout_exercise(
            session,
            w.id,
            WorkoutExerciseInput(
                exercise_id=bizepscurl.id,
                plan_exercise_id=None,
                sets=[WorkoutSetInput(weight=15.0 + i, reps=10, duration_time=None, is_warmup=False)],
            ),
        )
        w.completed_at = started + timedelta(minutes=45)
        session.commit()

    print("Seed abgeschlossen.")
    print(f"Exercises: {kniebeuge.name}, {kreuzheben.name}, {klimmzug.name}, {bizepscurl.name}, {plank.name}")
    print(f"Trainingsplan: {plan.name} (id={plan.id})")


if __name__ == "__main__":
    try:
        seed()
    finally:
        session.close()
