# TODO: WorkoutExerciseInput.name testet ein Feld, das nach Einführung von Exercise
# (WorkoutExercise hat kein eigenes name mehr) durch exercise_id ersetzt werden muss.
import pytest

from application.inputs.workout_exercise_input import WorkoutExerciseInput
from application.inputs.workout_set_input import WorkoutSetInput


def test_creates_valid_workout_exercise_input_with_empty_sets() -> None:
    ex = WorkoutExerciseInput(name="Bench Press", plan_exercise_id=None, sets=[])
    assert ex.name == "Bench Press"
    assert ex.plan_exercise_id is None
    assert ex.sets == []


def test_creates_valid_workout_exercise_input_with_sets() -> None:
    ex = WorkoutExerciseInput(
        name="Bench Press",
        plan_exercise_id=1,
        sets=[WorkoutSetInput(weight=80.0, reps=8, duration_time=None, is_warmup=False)],
    )
    assert ex.plan_exercise_id == 1
    assert len(ex.sets) == 1


def test_raises_for_empty_name() -> None:
    with pytest.raises(ValueError):
        WorkoutExerciseInput(name="  ", plan_exercise_id=None, sets=[])


def test_raises_for_sets_none() -> None:
    with pytest.raises(ValueError):
        WorkoutExerciseInput(name="Bench Press", plan_exercise_id=None, sets=None)  # type: ignore[arg-type]
