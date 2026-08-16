from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from application.inputs.analysis_inputs import RepData, TimeData, WeightData
from application.inputs.plan_exercise_input import PlanExerciseInput
from application.inputs.workout_exercise_input import WorkoutExerciseInput
from application.inputs.workout_set_input import WorkoutSetInput
from application.training_plan import create_training_plan
from application.workout import (
    add_workout_exercise,
    add_workout_set,
    create_workout,
    end_workout,
    get_workout,
    remove_workout_exercise,
    remove_workout_set,
    remove_workout,
    save_as_training_plan,
    update_workout_exercise,
    update_workout_set,
    get_best_weight_per_workout_by_exercise_id,
    get_best_reps_per_workout_by_exercise_id,
    get_best_time_per_workout_by_exercise_id
)
from models.exercise import Exercise


def _create_exercise(session, name: str) -> int:
    exercise = Exercise(name=name)
    session.add(exercise)
    session.flush()
    return exercise.id


def _rep_plan_input(session, name: str, weight: float) -> PlanExerciseInput:
    return PlanExerciseInput(
        exercise_id=_create_exercise(session, name),
        targeted_weight=weight,
        min_targeted_reps=8,
        max_targeted_reps=12,
        min_duration_time=None,
        max_duration_time=None,
        rest_sec=90.0,
    )


def _workout_ex(exercise_id: int, plan_exercise_id: int | None, sets: list[WorkoutSetInput]) -> WorkoutExerciseInput:
    return WorkoutExerciseInput(
        exercise_id=exercise_id,
        plan_exercise_id=plan_exercise_id,
        sets=sets,
    )


def _create_plan(session):
    plan = create_training_plan(session, "P", [_rep_plan_input(session, "Bench", 80.0), _rep_plan_input(session, "Row", 70.0)])
    assert len(plan.plan_exercises) == 2
    return plan


def _create_completed_workout(session, name: str, started_at: datetime, completed_at: datetime | None):
    w = create_workout(session, name=name, training_plan_id=None, started_at=started_at)
    if completed_at is not None:
        w.completed_at = completed_at
        session.commit()
    return w


def test_create_workout_without_plan_sets_started_at_and_completed_none(session) -> None:
    started = datetime.now() - timedelta(days=1)
    w = create_workout(session, name="W1", training_plan_id=None, started_at=started)
    assert w.id is not None
    assert w.training_plan_id is None
    assert w.started_at == started
    assert w.completed_at is None


def test_create_workout_with_plan_requires_existing_plan(session) -> None:
    with pytest.raises(ValueError):
        create_workout(session, name="W", training_plan_id=9999, started_at=None)


def test_add_workout_exercise_without_plan_disallows_plan_exercise_reference(session) -> None:
    w = create_workout(session, name="W", training_plan_id=None, started_at=None)
    bench_id = _create_exercise(session, "Bench")

    with pytest.raises(ValueError):
        add_workout_exercise(
            session,
            w.id,
            _workout_ex(bench_id, 1, sets=[WorkoutSetInput(weight=80.0, reps=8, duration_time=None, is_warmup=False)]),
        )

    w = add_workout_exercise(
        session,
        w.id,
        _workout_ex(bench_id, None, sets=[WorkoutSetInput(weight=80.0, reps=8, duration_time=None, is_warmup=True)]),
    )

    assert len(w.workout_exercises) == 1
    ex = w.workout_exercises[0]
    assert ex.plan_exercise_id is None
    assert len(ex.sets) == 1
    assert ex.sets[0].isWarmup is True


def test_add_workout_exercise_with_plan_requires_plan_exercise_id_and_belongs_to_plan(session) -> None:
    plan = _create_plan(session)
    w = create_workout(session, name="W", training_plan_id=plan.id, started_at=None)
    bench_exercise_id = plan.plan_exercises[0].exercise_id

    # bound workout -> must reference plan_exercise
    with pytest.raises(ValueError):
        add_workout_exercise(
            session,
            w.id,
            _workout_ex(bench_exercise_id, None, sets=[WorkoutSetInput(weight=80.0, reps=8, duration_time=None, is_warmup=False)]),
        )

    # wrong plan_exercise_id
    with pytest.raises(ValueError):
        add_workout_exercise(
            session,
            w.id,
            _workout_ex(bench_exercise_id, 9999, sets=[WorkoutSetInput(weight=80.0, reps=8, duration_time=None, is_warmup=False)]),
        )

    # valid
    bench_plan_id = plan.plan_exercises[0].id
    w = add_workout_exercise(
        session,
        w.id,
        _workout_ex(
            bench_exercise_id,
            bench_plan_id,
            sets=[
                WorkoutSetInput(weight=60.0, reps=5, duration_time=None, is_warmup=True),
                WorkoutSetInput(weight=80.0, reps=8, duration_time=None, is_warmup=False),
            ],
        ),
    )
    assert len(w.workout_exercises) == 1
    assert w.workout_exercises[0].plan_exercise_id == bench_plan_id
    assert [s.isWarmup for s in w.workout_exercises[0].sets] == [True, False]


def test_update_and_remove_workout_exercise(session) -> None:
    plan = _create_plan(session)
    w = create_workout(session, name="W", training_plan_id=plan.id, started_at=None)
    bench_exercise_id = plan.plan_exercises[0].exercise_id
    bench_id = plan.plan_exercises[0].id
    row_exercise_id = plan.plan_exercises[1].exercise_id
    row_id = plan.plan_exercises[1].id

    w = add_workout_exercise(
        session,
        w.id,
        _workout_ex(bench_exercise_id, bench_id, sets=[WorkoutSetInput(weight=80.0, reps=8, duration_time=None, is_warmup=False)]),
    )
    w = add_workout_exercise(
        session,
        w.id,
        _workout_ex(row_exercise_id, row_id, sets=[WorkoutSetInput(weight=70.0, reps=10, duration_time=None, is_warmup=False)]),
    )

    # update in place + remap sets
    ex_to_update = w.workout_exercises[0]
    ex_id = ex_to_update.id
    w = update_workout_exercise(
        session,
        w.id,
        ex_id,
        _workout_ex(
            bench_exercise_id,
            bench_id,
            sets=[
                WorkoutSetInput(weight=80.0, reps=9, duration_time=None, is_warmup=False),
                WorkoutSetInput(weight=80.0, reps=8, duration_time=None, is_warmup=False),
            ],
        ),
    )
    updated = next(ex for ex in w.workout_exercises if ex.id == ex_id)
    assert len(updated.sets) == 2

    # remove second
    second_id = w.workout_exercises[1].id
    w = remove_workout_exercise(session, w.id, second_id)
    assert len(w.workout_exercises) == 1


def test_add_update_remove_workout_set(session) -> None:
    w = create_workout(session, name="W", training_plan_id=None, started_at=None)
    bench_id = _create_exercise(session, "Bench")
    w = add_workout_exercise(
        session,
        w.id,
        _workout_ex(bench_id, None, sets=[WorkoutSetInput(weight=80.0, reps=8, duration_time=None, is_warmup=False)]),
    )
    ex_id = w.workout_exercises[0].id

    w = add_workout_set(session, w.id, ex_id, WorkoutSetInput(weight=80.0, reps=9, duration_time=None, is_warmup=False))
    assert len(w.workout_exercises[0].sets) == 2

    set_id = w.workout_exercises[0].sets[0].id
    w = update_workout_set(
        session,
        w.id,
        ex_id,
        set_id,
        WorkoutSetInput(weight=82.5, reps=6, duration_time=None, is_warmup=True),
    )
    updated = next(s for s in w.workout_exercises[0].sets if s.id == set_id)
    assert updated.weight == 82.5
    assert updated.reps == 6
    assert updated.isWarmup is True

    w = remove_workout_set(session, w.id, ex_id, set_id)
    assert all(s.id != set_id for s in w.workout_exercises[0].sets)


def test_end_workout_sets_completed_at(session) -> None:
    w = create_workout(session, name="W", training_plan_id=None, started_at=None)
    assert w.completed_at is None
    w = end_workout(session, w.id)
    assert w.completed_at is not None


def test_save_workout_as_training_plan(session) -> None:
    w = create_workout(session, name="Template", training_plan_id=None, started_at=None)
    bench_id = _create_exercise(session, "Bench")
    plank_id = _create_exercise(session, "Plank")
    w = add_workout_exercise(
        session,
        w.id,
        _workout_ex(
            bench_id,
            None,
            sets=[
                WorkoutSetInput(weight=60.0, reps=5, duration_time=None, is_warmup=True),
                WorkoutSetInput(weight=80.0, reps=8, duration_time=None, is_warmup=False),
            ],
        ),
    )
    w = add_workout_exercise(
        session,
        w.id,
        _workout_ex(plank_id, None, sets=[WorkoutSetInput(weight=None, reps=None, duration_time=60.0, is_warmup=False)]),
    )

    plan = save_as_training_plan(session, w.id)
    assert plan.id is not None
    assert plan.name == "Template"
    assert [ex.exercise.name for ex in plan.plan_exercises] == ["Bench", "Plank"]


def test_save_workout_as_training_plan_raises_if_only_warmups(session) -> None:
    w = create_workout(session, name="Bad", training_plan_id=None, started_at=None)
    bench_id = _create_exercise(session, "Bench")
    w = add_workout_exercise(
        session,
        w.id,
        _workout_ex(bench_id, None, sets=[WorkoutSetInput(weight=60.0, reps=5, duration_time=None, is_warmup=True)]),
    )

    with pytest.raises(ValueError):
        save_as_training_plan(session, w.id)


def test_remove_workout_deletes_aggregate(session) -> None:
    w = create_workout(session, name="W", training_plan_id=None, started_at=None)
    remove_workout(session, w.id)
    with pytest.raises(ValueError):
        get_workout(session, w.id)


def test_get_best_weight_per_workout_by_exercise_id_returns_empty_list_without_data(session) -> None:
    exercise = _create_exercise(session, "Curl")

    result = get_best_weight_per_workout_by_exercise_id(session, exercise, None, None)

    assert result == []


def test_get_best_weight_per_workout_by_exercise_id_picks_max_weight_and_ignores_warmups(session) -> None:
    exercise_id = _create_exercise(session, "Curl")
    day1 = datetime(2026, 1, 1)
    w1 = _create_completed_workout(session, "W1", started_at=day1, completed_at=day1)
    w1 = add_workout_exercise(
        session,
        w1.id,
        _workout_ex(
            exercise_id,
            None,
            sets=[
                WorkoutSetInput(weight=100.0, reps=1, duration_time=None, is_warmup=True),
                WorkoutSetInput(weight=40.0, reps=8, duration_time=None, is_warmup=False),
                WorkoutSetInput(weight=45.0, reps=6, duration_time=None, is_warmup=False),
            ],
        ),
    )

    result = get_best_weight_per_workout_by_exercise_id(session, exercise_id, None, None)

    assert result == [WeightData(completed_at=day1, weight=45.0)]


def test_get_best_weight_per_workout_by_exercise_id_excludes_incomplete_and_other_exercise_workouts(session) -> None:
    exercise_id = _create_exercise(session, "Curl")
    other_exercise_id = _create_exercise(session, "Press")
    day1 = datetime(2026, 1, 1)

    incomplete = create_workout(session, name="Incomplete", training_plan_id=None, started_at=day1)
    add_workout_exercise(
        session,
        incomplete.id,
        _workout_ex(exercise_id, None, sets=[WorkoutSetInput(weight=99.0, reps=5, duration_time=None, is_warmup=False)]),
    )

    other = _create_completed_workout(session, "Other", started_at=day1, completed_at=day1)
    add_workout_exercise(
        session,
        other.id,
        _workout_ex(other_exercise_id, None, sets=[WorkoutSetInput(weight=99.0, reps=5, duration_time=None, is_warmup=False)]),
    )

    result = get_best_weight_per_workout_by_exercise_id(session, exercise_id, None, None)

    assert result == []


def test_get_best_weight_per_workout_by_exercise_id_orders_by_date_and_filters_by_range(session) -> None:
    exercise_id = _create_exercise(session, "Curl")
    day1 = datetime(2026, 1, 1)
    day2 = datetime(2026, 1, 8)
    day3 = datetime(2026, 1, 15)

    for day, weight in [(day2, 50.0), (day1, 40.0), (day3, 60.0)]:
        w = _create_completed_workout(session, f"W-{day.isoformat()}", started_at=day, completed_at=day)
        add_workout_exercise(
            session,
            w.id,
            _workout_ex(exercise_id, None, sets=[WorkoutSetInput(weight=weight, reps=5, duration_time=None, is_warmup=False)]),
        )

    all_points = get_best_weight_per_workout_by_exercise_id(session, exercise_id, None, None)
    assert all_points == [
        WeightData(completed_at=day1, weight=40.0),
        WeightData(completed_at=day2, weight=50.0),
        WeightData(completed_at=day3, weight=60.0),
    ]

    ranged = get_best_weight_per_workout_by_exercise_id(session, exercise_id, day1 + timedelta(days=1), day3 - timedelta(days=1))
    assert ranged == [WeightData(completed_at=day2, weight=50.0)]


def test_get_best_reps_per_workout_by_exercise_id_returns_empty_list_without_data(session) -> None:
    exercise = _create_exercise(session, "Curl")

    result = get_best_reps_per_workout_by_exercise_id(session, exercise, weight=50.0)

    assert result == []


def test_get_best_reps_per_workout_by_exercise_id_filters_by_weight_class_and_ignores_warmups(session) -> None:
    exercise_id = _create_exercise(session, "Curl")
    day1 = datetime(2026, 1, 1)
    w = _create_completed_workout(session, "W1", started_at=day1, completed_at=day1)
    add_workout_exercise(
        session,
        w.id,
        _workout_ex(
            exercise_id,
            None,
            sets=[
                WorkoutSetInput(weight=50.0, reps=20, duration_time=None, is_warmup=True),
                WorkoutSetInput(weight=50.0, reps=8, duration_time=None, is_warmup=False),
                WorkoutSetInput(weight=50.0, reps=10, duration_time=None, is_warmup=False),
                WorkoutSetInput(weight=60.0, reps=15, duration_time=None, is_warmup=False),
            ],
        ),
    )

    result = get_best_reps_per_workout_by_exercise_id(session, exercise_id, weight=50.0)

    assert result == [RepData(completed_at=day1, reps=10)]


def test_get_best_reps_per_workout_by_exercise_id_normalizes_weight_to_nearest_eighth(session) -> None:
    exercise_id = _create_exercise(session, "Curl")
    day1 = datetime(2026, 1, 1)
    w = _create_completed_workout(session, "W1", started_at=day1, completed_at=day1)
    add_workout_exercise(
        session,
        w.id,
        _workout_ex(exercise_id, None, sets=[WorkoutSetInput(weight=50.06, reps=7, duration_time=None, is_warmup=False)]),
    )

    result = get_best_reps_per_workout_by_exercise_id(session, exercise_id, weight=50.0)

    assert result == [RepData(completed_at=day1, reps=7)]


def test_get_best_reps_per_workout_by_exercise_id_none_weight_matches_only_bodyweight_sets(session) -> None:
    exercise_id = _create_exercise(session, "Pull-Up")
    day1 = datetime(2026, 1, 1)
    w = _create_completed_workout(session, "W1", started_at=day1, completed_at=day1)
    add_workout_exercise(
        session,
        w.id,
        _workout_ex(
            exercise_id,
            None,
            sets=[
                WorkoutSetInput(weight=None, reps=12, duration_time=None, is_warmup=False),
                WorkoutSetInput(weight=10.0, reps=5, duration_time=None, is_warmup=False),
            ],
        ),
    )

    result = get_best_reps_per_workout_by_exercise_id(session, exercise_id, weight=None)

    assert result == [RepData(completed_at=day1, reps=12)]


def test_get_best_time_per_workout_by_exercise_id_returns_empty_list_without_data(session) -> None:
    exercise = _create_exercise(session, "Plank")

    result = get_best_time_per_workout_by_exercise_id(session, exercise, weight=None)

    assert result == []


def test_get_best_time_per_workout_by_exercise_id_picks_max_duration_for_bodyweight_and_ignores_warmups(session) -> None:
    exercise_id = _create_exercise(session, "Plank")
    day1 = datetime(2026, 1, 1)
    w = _create_completed_workout(session, "W1", started_at=day1, completed_at=day1)
    add_workout_exercise(
        session,
        w.id,
        _workout_ex(
            exercise_id,
            None,
            sets=[
                WorkoutSetInput(weight=None, reps=None, duration_time=120.0, is_warmup=True),
                WorkoutSetInput(weight=None, reps=None, duration_time=60.0, is_warmup=False),
                WorkoutSetInput(weight=None, reps=None, duration_time=90.0, is_warmup=False),
            ],
        ),
    )

    result = get_best_time_per_workout_by_exercise_id(session, exercise_id, weight=None)

    assert result == [TimeData(completed_at=day1, duration_time=90.0)]


def test_get_best_time_per_workout_by_exercise_id_filters_by_weight_class(session) -> None:
    exercise_id = _create_exercise(session, "Weighted Plank")
    day1 = datetime(2026, 1, 1)
    w = _create_completed_workout(session, "W1", started_at=day1, completed_at=day1)
    add_workout_exercise(
        session,
        w.id,
        _workout_ex(
            exercise_id,
            None,
            sets=[
                WorkoutSetInput(weight=20.0, reps=None, duration_time=45.0, is_warmup=False),
                WorkoutSetInput(weight=10.0, reps=None, duration_time=75.0, is_warmup=False),
            ],
        ),
    )

    result = get_best_time_per_workout_by_exercise_id(session, exercise_id, weight=20.0)

    assert result == [TimeData(completed_at=day1, duration_time=45.0)]