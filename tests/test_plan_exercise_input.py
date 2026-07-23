# TODO: PlanExerciseInput.name testet ein Feld, das nach Einführung von Exercise
# (PlanExercise hat kein eigenes name mehr) durch exercise_id ersetzt werden muss.
import pytest
from application.inputs.plan_exercise_input import PlanExerciseInput

def test_creates_valid_rep_based_plan_exercise_input() -> None:
    plan_exercise = PlanExerciseInput(
        name="Bench Press",
        targeted_weight=80.0,
        min_targeted_reps=8,
        max_targeted_reps=12,
        min_duration_time=None,
        max_duration_time=None,
        rest_sec=90.0,
    )

    assert plan_exercise.name == "Bench Press"
    assert plan_exercise.min_targeted_reps == 8
    assert plan_exercise.max_targeted_reps == 12

def test_raises_for_empty_name() -> None:
    with pytest.raises(ValueError):
        PlanExerciseInput(
            name="   ",
            targeted_weight=None,
            min_targeted_reps=8,
            max_targeted_reps=12,
            min_duration_time=None,
            max_duration_time=None,
            rest_sec=60.0,
        )

def test_creates_valid_duration_based_exercise_input() -> None:
    plan_exercise = PlanExerciseInput(
        name="Plank",
        targeted_weight=None,
        min_targeted_reps=None,
        max_targeted_reps=None,
        min_duration_time=13,
        max_duration_time=25,
        rest_sec=180,
    )

    assert plan_exercise.name == "Plank"
    assert plan_exercise.min_duration_time == 13
    assert plan_exercise.max_duration_time == 25

def test_raises_for_both_exercise_types_not_set() -> None:
    with pytest.raises(ValueError):
        PlanExerciseInput(
            name="Klimzüge",
            targeted_weight=None,
            min_targeted_reps=None,
            max_targeted_reps=None,
            min_duration_time=None,
            max_duration_time=None,
            rest_sec=60.0,
        )


def test_raises_for_both_exercise_types_set() -> None:
    with pytest.raises(ValueError):
        PlanExerciseInput(
            name="Klimzüge",
            targeted_weight=None,
            min_targeted_reps=10,
            max_targeted_reps=15,
            min_duration_time=2,
            max_duration_time=7,
            rest_sec=60.0,
        )

def test_raises_for_min_set_max_not_set_for_reps() -> None:
    with pytest.raises(ValueError):
        PlanExerciseInput(
            name="Klimzüge",
            targeted_weight=None,
            min_targeted_reps=10,
            max_targeted_reps=None,
            min_duration_time=None,
            max_duration_time=None,
            rest_sec=60.0,
        )

def test_raises_for_min_set_max_not_set_for_duration() -> None:
    with pytest.raises(ValueError):
        PlanExerciseInput(
            name="Klimzüge",
            targeted_weight=None,
            min_targeted_reps=None,
            max_targeted_reps=None,
            min_duration_time=9,
            max_duration_time=None,
            rest_sec=60.0,
        )

def test_raises_for_max_set_min_not_set_for_duration() -> None:
    with pytest.raises(ValueError):
        PlanExerciseInput(
            name="Klimzüge",
            targeted_weight=None,
            min_targeted_reps=None,
            max_targeted_reps=None,
            min_duration_time=None,
            max_duration_time=7,
            rest_sec=60.0,
        )


def test_raises_for_min_greater_max_reps() -> None:
    with pytest.raises(ValueError):
        PlanExerciseInput(
            name="Klimzüge",
            targeted_weight=None,
            min_targeted_reps=12,
            max_targeted_reps=1,
            min_duration_time=None,
            max_duration_time=None,
            rest_sec=60.0,
        )

def test_raises_for_min_greater_max_duration() -> None:
    with pytest.raises(ValueError):
        PlanExerciseInput(
            name="Klimzüge",
            targeted_weight=None,
            min_targeted_reps=None,
            max_targeted_reps=None,
            min_duration_time=34,
            max_duration_time=1,
            rest_sec=60.0,
        )

def test_raises_for_negative_values() -> None:
    with pytest.raises(ValueError):
        PlanExerciseInput(
            name="Klimzüge",
            targeted_weight=None,
            min_targeted_reps=None,
            max_targeted_reps=None,
            min_duration_time=-34,
            max_duration_time=1,
            rest_sec=60.0,
        )
