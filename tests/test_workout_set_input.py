import pytest

from application.inputs.workout_set_input import WorkoutSetInput


def test_creates_valid_rep_based_workout_set_input() -> None:
    s = WorkoutSetInput(weight=80.0, reps=8, duration_time=None, is_warmup=False)
    assert s.weight == 80.0
    assert s.reps == 8
    assert s.duration_time is None
    assert s.is_warmup is False


def test_creates_valid_duration_based_workout_set_input() -> None:
    s = WorkoutSetInput(weight=None, reps=None, duration_time=60.0, is_warmup=True)
    assert s.weight is None
    assert s.reps is None
    assert s.duration_time == 60.0
    assert s.is_warmup is True


@pytest.mark.parametrize(
    "reps,duration_time",
    [
        (None, None),
        (10, 60.0),
    ],
)
def test_raises_when_rep_or_duration_rule_is_violated(reps, duration_time) -> None:
    with pytest.raises(ValueError):
        WorkoutSetInput(weight=None, reps=reps, duration_time=duration_time, is_warmup=False)


@pytest.mark.parametrize(
    "weight,reps,duration_time",
    [
        (-0.1, 10, None),
        (0.0, 0, None),
        (0.0, -1, None),
        (0.0, None, 0.0),
        (0.0, None, -3.0),
    ],
)
def test_raises_for_invalid_non_positive_or_negative_values(weight, reps, duration_time) -> None:
    with pytest.raises(ValueError):
        WorkoutSetInput(weight=weight, reps=reps, duration_time=duration_time, is_warmup=False)
