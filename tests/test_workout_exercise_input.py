import pytest

from application.inputs.workout_exercise_input import WorkoutExerciseInput
from application.inputs.workout_set_input import WorkoutSetInput


def test_creates_valid_workout_exercise_input_with_empty_sets() -> None:
    ex = WorkoutExerciseInput(exercise_id=1, plan_exercise_id=None, sets=[])
    assert ex.exercise_id == 1
    assert ex.plan_exercise_id is None
    assert ex.sets == []


def test_creates_valid_workout_exercise_input_with_sets() -> None:
    ex = WorkoutExerciseInput(
        exercise_id=1,
        plan_exercise_id=1,
        sets=[WorkoutSetInput(weight=80.0, reps=8, duration_time=None, is_warmup=False)],
    )
    assert ex.plan_exercise_id == 1
    assert len(ex.sets) == 1


def test_raises_for_missing_exercise_id() -> None:
    with pytest.raises(ValueError):
        WorkoutExerciseInput(exercise_id=0, plan_exercise_id=None, sets=[])


def test_raises_for_sets_none() -> None:
    with pytest.raises(ValueError):
        WorkoutExerciseInput(exercise_id=1, plan_exercise_id=None, sets=None)  # type: ignore[arg-type]
