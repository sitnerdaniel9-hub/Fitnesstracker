import pytest
from application.training_plan import create_training_plan
from application.inputs.plan_exercise_input import PlanExerciseInput

def test_create_training_plan(session) -> None:
    exercises : list[PlanExerciseInput] = []
    plan_exercise1 = PlanExerciseInput(
        name="Bench Press",
        targeted_weight=80.0,
        min_targeted_reps=8,
        max_targeted_reps=12,
        min_duration_time=None,
        max_duration_time=None,
        rest_sec=90.0,
    )
    plan_exercise2 = PlanExerciseInput(
        name="Shoulder Press",
        targeted_weight=60.0,
        min_targeted_reps=8,
        max_targeted_reps=12,
        min_duration_time=None,
        max_duration_time=None,
        rest_sec=90.0,
    )
    plan_exercise3 = PlanExerciseInput(
        name="Plank",
        targeted_weight=None,
        min_targeted_reps=None,
        max_targeted_reps=None,
        min_duration_time=60,
        max_duration_time=90,
        rest_sec=90.0,
    )
    exercises.append(plan_exercise1)
    exercises.append(plan_exercise2)
    exercises.append(plan_exercise3)
    training_plan = create_training_plan(session, "Upper Body", exercises)

    assert training_plan is not None
    assert training_plan.name == "Upper Body"
    assert len(training_plan.plan_exercises) == 3

    first_exercise = training_plan.plan_exercises[0]

    assert first_exercise.name == "Bench Press"
    assert first_exercise.order_index == 1
    assert first_exercise.targeted_weight == 80.0
    assert first_exercise.min_targeted_reps == 8
    assert first_exercise.max_targeted_reps == 12
    assert first_exercise.min_targeted_duration_time is None
    assert first_exercise.max_targeted_duration_time is None
    assert first_exercise.break_time == 90.0

    third_exercise = training_plan.plan_exercises[2]

    assert third_exercise.name == "Plank"
    assert third_exercise.order_index == 3
    assert third_exercise.targeted_weight is None
    assert third_exercise.min_targeted_reps is None
    assert third_exercise.max_targeted_reps is None
    assert third_exercise.min_targeted_duration_time == 60.0
    assert third_exercise.max_targeted_duration_time == 90.0
    assert third_exercise.break_time == 90.0


def test_create_training_plan_allows_empty_exercises(session) -> None:
    training_plan = create_training_plan(session, "Empty Plan", [])

    assert training_plan is not None
    assert training_plan.name == "Empty Plan"
    assert len(training_plan.plan_exercises) == 0


def test_create_training_plan_raises_for_empty_name(session) -> None:
    with pytest.raises(ValueError):
        create_training_plan(session, "   ", [])