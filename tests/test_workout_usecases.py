from __future__ import annotations

from datetime import datetime, timedelta

import pytest

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
