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


# TODO: create_training_plan/add_workout_exercise rufen intern PlanExercise(name=...)/
# WorkoutExercise(name=...) auf, was seit Einführung von Exercise (exercise_id statt name)
# nicht mehr funktioniert. Betrifft alle Tests in dieser Datei, die diese Funktionen aufrufen.
def _plan_ex(name: str) -> PlanExerciseInput:
    return PlanExerciseInput(
        name=name,
        targeted_weight=80.0,
        min_targeted_reps=8,
        max_targeted_reps=12,
        min_duration_time=None,
        max_duration_time=None,
        rest_sec=90.0,
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
    plan = create_training_plan(session, "P", [_plan_ex("Bench")])
    pe_id = plan.plan_exercises[0].id

    w1 = create_workout(session, "W1", training_plan_id=plan.id, started_at=datetime(2026, 1, 1, 10, 0, 0))
    add_workout_exercise(
        session,
        w1.id,
        WorkoutExerciseInput(
            name="Bench",
            plan_exercise_id=pe_id,
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
        WorkoutExerciseInput(
            name="Bench",
            plan_exercise_id=pe_id,
            sets=[
                WorkoutSetInput(weight=85.0, reps=5, duration_time=None, is_warmup=False),
                WorkoutSetInput(weight=85.0, reps=6, duration_time=None, is_warmup=False),
            ],
        ),
    )

    best = get_pr_for_exercise(session, pe_id)
    assert best is not None
    # höchste Last: 85.0; tie-breaker: 6 reps
    assert best.weight == 85.0
    assert best.reps == 6


def test_get_avg_weight_gain_uses_max_per_workout_and_only_completed(session) -> None:
    plan = create_training_plan(session, "P", [_plan_ex("Bench")])
    pe_id = plan.plan_exercises[0].id

    def make_workout(day: int, max_weight: float, completed: bool = True):
        started = datetime(2026, 1, 1 + day, 10, 0, 0)
        w = create_workout(session, f"W{day}", training_plan_id=plan.id, started_at=started)
        add_workout_exercise(
            session,
            w.id,
            WorkoutExerciseInput(
                name="Bench",
                plan_exercise_id=pe_id,
                sets=[
                    WorkoutSetInput(weight=max_weight - 5, reps=8, duration_time=None, is_warmup=False),
                    WorkoutSetInput(weight=max_weight, reps=6, duration_time=None, is_warmup=False),
                    WorkoutSetInput(weight=max_weight + 20, reps=1, duration_time=None, is_warmup=True),
                ],
            ),
        )
        if completed:
            w.completed_at = started + timedelta(hours=1)
            session.commit()
        return w

    make_workout(0, 80.0, completed=True)
    make_workout(1, 82.5, completed=True)
    make_workout(2, 85.0, completed=True)
    make_workout(3, 90.0, completed=False)  # wird ignoriert

    gain = get_avg_weight_gain(session, pe_id)
    # Differenzen: 2.5 + 2.5 => avg 2.5
    assert gain == pytest.approx(2.5)


def test_get_avg_weight_gain_returns_none_for_less_than_two_points(session) -> None:
    plan = create_training_plan(session, "P", [_plan_ex("Bench")])
    pe_id = plan.plan_exercises[0].id
    w = create_workout(session, "W", training_plan_id=plan.id, started_at=datetime(2026, 1, 1, 10, 0, 0))
    add_workout_exercise(
        session,
        w.id,
        WorkoutExerciseInput(
            name="Bench",
            plan_exercise_id=pe_id,
            sets=[WorkoutSetInput(weight=80.0, reps=8, duration_time=None, is_warmup=False)],
        ),
    )
    w.completed_at = datetime(2026, 1, 1, 11, 0, 0)
    session.commit()

    assert get_avg_weight_gain(session, pe_id) is None


def test_normalize_weight_rounds_to_0_125_steps() -> None:
    assert normalize_weight(50.01) == 50.0
    assert normalize_weight(50.06) == 50.0
    assert normalize_weight(50.07) == 50.125


def test_get_avg_rep_increase_for_weight_class(session) -> None:
    plan = create_training_plan(session, "P", [_plan_ex("Bench")])
    pe_id = plan.plan_exercises[0].id

    base = datetime(2026, 1, 1, 10, 0, 0)
    for i, reps in enumerate([8, 9, 10]):
        w = create_workout(session, f"W{i}", training_plan_id=plan.id, started_at=base + timedelta(days=i))
        add_workout_exercise(
            session,
            w.id,
            WorkoutExerciseInput(
                name="Bench",
                plan_exercise_id=pe_id,
                sets=[
                    WorkoutSetInput(weight=50.01, reps=reps, duration_time=None, is_warmup=False),
                    WorkoutSetInput(weight=50.01, reps=reps - 1, duration_time=None, is_warmup=False),
                ],
            ),
        )
        w.completed_at = base + timedelta(days=i, hours=1)
        session.commit()

    inc = get_avg_rep_increase(session, pe_id, weight=50.0)
    assert inc == pytest.approx(1.0)


def test_get_avg_time_increase_for_weightless_time_exercise(session) -> None:
    # Zeitübung ohne Gewicht (weight=None)
    plan = create_training_plan(
        session,
        "P",
        [
            PlanExerciseInput(
                name="Plank",
                targeted_weight=None,
                min_targeted_reps=None,
                max_targeted_reps=None,
                min_duration_time=30.0,
                max_duration_time=60.0,
                rest_sec=60.0,
            )
        ],
    )
    pe_id = plan.plan_exercises[0].id

    base = datetime(2026, 1, 1, 10, 0, 0)
    for i, secs in enumerate([30.0, 45.0, 60.0]):
        w = create_workout(session, f"W{i}", training_plan_id=plan.id, started_at=base + timedelta(days=i))
        add_workout_exercise(
            session,
            w.id,
            WorkoutExerciseInput(
                name="Plank",
                plan_exercise_id=pe_id,
                sets=[
                    WorkoutSetInput(weight=None, reps=None, duration_time=secs, is_warmup=False),
                    WorkoutSetInput(weight=None, reps=None, duration_time=secs - 5.0, is_warmup=False),
                ],
            ),
        )
        w.completed_at = base + timedelta(days=i, hours=1)
        session.commit()

    inc = get_avg_time_increase(session, pe_id, weight=None)
    # Best per workout: 30,45,60 => diffs 15+15 /2 => 15
    assert inc == pytest.approx(15.0)
