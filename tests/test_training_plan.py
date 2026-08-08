import pytest
from application.training_plan import (
    add_plan_exercise,
    create_training_plan,
    find_training_plan_by_id,
    find_training_plans_by_name,
    get_all_training_plans,
    remove_plan_exercise,
    reorder_plan_exercise,
    rename_training_plan,
    toggle_training_plan_status,
    update_plan_exercise,
)
from application.inputs.plan_exercise_input import PlanExerciseInput
from models.exercise import Exercise


def _create_exercise(session, name: str) -> int:
    exercise = Exercise(name=name)
    session.add(exercise)
    session.flush()
    return exercise.id


def _rep_input(session, name: str, weight: float, min_reps: int, max_reps: int) -> PlanExerciseInput:
    return PlanExerciseInput(
        exercise_id=_create_exercise(session, name),
        targeted_weight=weight,
        min_targeted_reps=min_reps,
        max_targeted_reps=max_reps,
        min_duration_time=None,
        max_duration_time=None,
        rest_sec=90.0,
    )


def _create_plan_with_three(session):
    plan = create_training_plan(
        session,
        "Plan A",
        [
            _rep_input(session, "Bench", 80.0, 8, 12),
            _rep_input(session, "Row", 70.0, 8, 12),
            _rep_input(session, "Squat", 120.0, 5, 8),
        ],
    )
    assert plan.id is not None
    assert len(plan.plan_exercises) == 3
    return plan

def test_create_training_plan(session) -> None:
    exercises : list[PlanExerciseInput] = []
    plan_exercise1 = PlanExerciseInput(
        exercise_id=_create_exercise(session, "Bench Press"),
        targeted_weight=80.0,
        min_targeted_reps=8,
        max_targeted_reps=12,
        min_duration_time=None,
        max_duration_time=None,
        rest_sec=90.0,
    )
    plan_exercise2 = PlanExerciseInput(
        exercise_id=_create_exercise(session, "Shoulder Press"),
        targeted_weight=60.0,
        min_targeted_reps=8,
        max_targeted_reps=12,
        min_duration_time=None,
        max_duration_time=None,
        rest_sec=90.0,
    )
    plan_exercise3 = PlanExerciseInput(
        exercise_id=_create_exercise(session, "Plank"),
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

    assert first_exercise.exercise.name == "Bench Press"
    assert first_exercise.order_index == 1
    assert first_exercise.targeted_weight == 80.0
    assert first_exercise.min_targeted_reps == 8
    assert first_exercise.max_targeted_reps == 12
    assert first_exercise.min_targeted_duration_time is None
    assert first_exercise.max_targeted_duration_time is None
    assert first_exercise.break_time == 90.0

    third_exercise = training_plan.plan_exercises[2]

    assert third_exercise.exercise.name == "Plank"
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

def test_add_plan_exercise_appends_with_next_order_index(session) -> None:
    plan = _create_plan_with_three(session)
    new_exercise = add_plan_exercise(session, plan.id, _rep_input(session, "Deadlift", 140.0, 3, 5))

    plan = find_training_plan_by_id(session, plan.id)
    assert len(plan.plan_exercises) == 4
    assert new_exercise.exercise.name == "Deadlift"
    assert new_exercise.order_index == 4


def test_remove_plan_exercise_normalizes_order_index(session) -> None:
    plan = _create_plan_with_three(session)
    mid_id = plan.plan_exercises[1].id

    plan = remove_plan_exercise(session, plan.id, mid_id)

    assert [ex.exercise.name for ex in plan.plan_exercises] == ["Bench", "Squat"]
    assert [ex.order_index for ex in plan.plan_exercises] == [1, 2]


def test_update_plan_exercise_updates_in_place(session) -> None:
    plan = _create_plan_with_three(session)
    ex = plan.plan_exercises[0]
    ex_id = ex.id

    updated = _rep_input(session, "Bench Press", 82.5, 6, 10)
    same_ex = update_plan_exercise(session, plan.id, ex_id, updated)

    assert same_ex.exercise.name == "Bench Press"
    assert same_ex.targeted_weight == 82.5
    assert same_ex.min_targeted_reps == 6
    assert same_ex.max_targeted_reps == 10


def test_reorder_plan_exercise_moves_and_normalizes(session) -> None:
    plan = _create_plan_with_three(session)
    squat_id = plan.plan_exercises[2].id

    plan = reorder_plan_exercise(session, plan.id, squat_id, new_position=1)

    assert [ex.exercise.name for ex in plan.plan_exercises] == ["Squat", "Bench", "Row"]
    assert [ex.order_index for ex in plan.plan_exercises] == [1, 2, 3]


def test_reorder_plan_exercise_raises_for_invalid_position(session) -> None:
    plan = _create_plan_with_three(session)
    ex_id = plan.plan_exercises[0].id

    with pytest.raises(ValueError):
        reorder_plan_exercise(session, plan.id, ex_id, new_position=0)

    with pytest.raises(ValueError):
        reorder_plan_exercise(session, plan.id, ex_id, new_position=99)


def test_find_and_search_training_plans(session) -> None:
    p1 = create_training_plan(session, "Upper Body", [])
    p2 = create_training_plan(session, "Lower Body", [])

    fetched = find_training_plan_by_id(session, p1.id)
    assert fetched.id == p1.id
    assert fetched.name == "Upper Body"

    all_plans = get_all_training_plans(session)
    assert [p.name for p in all_plans] == ["Upper Body", "Lower Body"]

    found = find_training_plans_by_name(session, "body")
    assert {p.name for p in found} == {"Upper Body", "Lower Body"}


def test_rename_and_toggle_active(session) -> None:
    plan = create_training_plan(session, "Old Name", [])
    assert plan.active is True

    plan = rename_training_plan(session, plan.id, "New Name")
    assert plan.name == "New Name"

    plan = toggle_training_plan_status(session, plan.id)
    assert plan.active is False

    plan = toggle_training_plan_status(session, plan.id)
    assert plan.active is True
