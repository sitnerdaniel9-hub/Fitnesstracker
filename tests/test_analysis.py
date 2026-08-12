from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from application.analysis import (
    count_avg_workouts_per_week,
    count_workouts_in_date_range,
    get_avg_rep_increase,
    get_avg_time_increase,
    get_avg_weight_gain,
    get_pr_for_exercise,
    normalize_weight,
)
from application.inputs.plan_exercise_input import PlanExerciseInput
from application.inputs.workout_exercise_input import WorkoutExerciseInput
from application.inputs.workout_set_input import WorkoutSetInput
from application.training_plan import create_training_plan
from application.workout import add_workout_exercise, create_workout
from models.exercise import Exercise
from application.inputs.analysis_inputs import WeightData, TimeData, RepData


def _create_exercise(session, name: str) -> int:
    exercise = Exercise(name=name)
    session.add(exercise)
    session.flush()
    return exercise.id


def _plan_ex(session, name: str) -> PlanExerciseInput:
    return PlanExerciseInput(
        exercise_id=_create_exercise(session, name),
        targeted_weight=80.0,
        min_targeted_reps=8,
        max_targeted_reps=12,
        min_duration_time=None,
        max_duration_time=None,
        rest_sec=90.0,
    )


def _workout_ex(exercise_id: int, plan_exercise_id: int, sets: list[WorkoutSetInput]) -> WorkoutExerciseInput:
    return WorkoutExerciseInput(
        exercise_id=exercise_id,
        plan_exercise_id=plan_exercise_id,
        sets=sets,
    )


def _create_completed_workout(session, name: str, started_at: datetime, completed_at: datetime | None = None):
    w = create_workout(session, name=name, training_plan_id=None, started_at=started_at)
    if completed_at is not None:
        w.completed_at = completed_at
        session.commit()
    return w


def test_count_workouts_in_date_range(session) -> None:
    base = datetime(2026, 1, 1, 10, 0, 0)
    _create_completed_workout(session, "W1", base)
    _create_completed_workout(session, "W2", base + timedelta(days=1))
    _create_completed_workout(session, "W3", base + timedelta(days=10))

    assert count_workouts_in_date_range(session, base, base + timedelta(days=2)) == 2
    assert count_workouts_in_date_range(session, base, base + timedelta(days=20)) == 3


def test_count_avg_workouts_per_week_returns_zero_for_empty_db(session) -> None:
    assert count_avg_workouts_per_week(session) == 0.0


def test_count_avg_workouts_per_week_with_explicit_range(session) -> None:
    start = datetime(2026, 1, 1, 10, 0, 0)
    # 7 Tage inkl. Start/End -> weeks = 1.0
    for i in range(7):
        _create_completed_workout(session, f"W{i}", start + timedelta(days=i))

    end = start + timedelta(days=6, hours=1)
    assert count_avg_workouts_per_week(session, start=start, end=end) == pytest.approx(7.0)


def test_count_avg_workouts_per_week_raises_for_start_after_end(session) -> None:
    with pytest.raises(ValueError):
        count_avg_workouts_per_week(session, start=datetime(2026, 1, 2), end=datetime(2026, 1, 1))


def test_get_pr_for_exercise_uses_weight_then_tie_breaker_and_ignores_warmup(session) -> None:
    plan = create_training_plan(session, "P", [_plan_ex(session, "Bench")])
    pe = plan.plan_exercises[0]
    pe_id = pe.id

    w1 = create_workout(session, "W1", training_plan_id=plan.id, started_at=datetime(2026, 1, 1, 10, 0, 0))
    add_workout_exercise(
        session,
        w1.id,
        _workout_ex(
            pe.exercise_id,
            pe_id,
            sets=[
                WorkoutSetInput(weight=100.0, reps=1, duration_time=None, is_warmup=True),
                WorkoutSetInput(weight=80.0, reps=8, duration_time=None, is_warmup=False),
            ],
        ),
    )

    w2 = create_workout(session, "W2", training_plan_id=plan.id, started_at=datetime(2026, 1, 8, 10, 0, 0))
    add_workout_exercise(
        session,
        w2.id,
        _workout_ex(
            pe.exercise_id,
            pe_id,
            sets=[
                WorkoutSetInput(weight=85.0, reps=5, duration_time=None, is_warmup=False),
                WorkoutSetInput(weight=85.0, reps=6, duration_time=None, is_warmup=False),
            ],
        ),
    )

    best = get_pr_for_exercise(session, pe.exercise_id)
    assert best is not None
    # höchste Last: 85.0; tie-breaker: 6 reps
    assert best.weight == 85.0
    assert best.reps == 6


def test_get_pr_for_exercise_works_for_workout_exercise_without_plan(session) -> None:
    exercise_id = _create_exercise(session, "Curl")

    w1 = create_workout(session, "W1", training_plan_id=None, started_at=datetime(2026, 1, 1, 10, 0, 0))
    add_workout_exercise(
        session,
        w1.id,
        _workout_ex(
            exercise_id,
            None,
            sets=[
                WorkoutSetInput(weight=100.0, reps=1, duration_time=None, is_warmup=True),
                WorkoutSetInput(weight=20.0, reps=8, duration_time=None, is_warmup=False),
            ],
        ),
    )

    w2 = create_workout(session, "W2", training_plan_id=None, started_at=datetime(2026, 1, 8, 10, 0, 0))
    add_workout_exercise(
        session,
        w2.id,
        _workout_ex(
            exercise_id,
            None,
            sets=[WorkoutSetInput(weight=22.5, reps=6, duration_time=None, is_warmup=False)],
        ),
    )

    best = get_pr_for_exercise(session, exercise_id)
    assert best is not None
    assert best.weight == 22.5
    assert best.reps == 6


def test_get_avg_weight_gain() -> None:
    weight_data = [
        WeightData(datetime(2026, 1, 1), 20.0),
        WeightData(datetime(2026, 1, 2), 22.5),
        WeightData(datetime(2026, 1, 3), 25.0),
    ]

    assert get_avg_weight_gain(weight_data) == pytest.approx(2.5)

def test_get_avg_weight_gain_returns_none_for_less_than_two_points() -> None:
    assert get_avg_weight_gain([]) is None
    assert get_avg_weight_gain(
        [WeightData(datetime(2026, 1, 1), 20.0)]
    ) is None

def test_get_avg_weight_gain_sorts_by_completion_time() -> None:
    weight_data = [
        WeightData(datetime(2026, 1, 3), 25.0),
        WeightData(datetime(2026, 1, 1), 20.0),
        WeightData(datetime(2026, 1, 2), 22.5),
    ]

    assert get_avg_weight_gain(weight_data) == pytest.approx(2.5)

def test_normalize_weight() -> None:
    assert normalize_weight(50.01) == 50.0
    assert normalize_weight(50.06) == 50.0
    assert normalize_weight(50.07) == 50.125

def test_get_avg_rep_increase() -> None:
    rep_data = [
        RepData(datetime(2026, 1, 1), 8),
        RepData(datetime(2026, 1, 2), 9),
        RepData(datetime(2026, 1, 3), 10),
    ]

    assert get_avg_rep_increase(rep_data) == pytest.approx(1.0)

def test_get_avg_rep_increase_returns_none_for_less_than_two_points() -> None:
    assert get_avg_rep_increase([]) is None
    assert get_avg_rep_increase(
        [RepData(datetime(2026, 1, 1), 8)]
    ) is None

def test_get_avg_time_increase() -> None:
    time_data = [
        TimeData(datetime(2026, 1, 1), 30.0),
        TimeData(datetime(2026, 1, 2), 45.0),
        TimeData(datetime(2026, 1, 3), 60.0),
    ]

    assert get_avg_time_increase(time_data) == pytest.approx(15.0)

def test_get_avg_time_increase_returns_none_for_less_than_two_points() -> None:
    assert get_avg_time_increase([]) is None
    assert get_avg_time_increase(
        [TimeData(datetime(2026, 1, 1), 30.0)]
    ) is None

def test_get_avg_weight_gain_can_be_negative() -> None:
    weight_data = [
        WeightData(datetime(2026, 1, 1), 100.0),
        WeightData(datetime(2026, 1, 2), 90.0),
        WeightData(datetime(2026, 1, 3), 100.0),
    ]

    assert get_avg_weight_gain(weight_data) == pytest.approx(0.0)

