from dataclasses import dataclass
from application.inputs.workout_set_input import WorkoutSetInput
from application.inputs.plan_exercise_input import PlanExerciseInput

@dataclass(frozen=True)
class WorkoutExerciseInput:
    exercise_id: int
    plan_exercise_id: int | None
    sets: list[WorkoutSetInput]

    def __post_init__(self):
        if not self.exercise_id:
            raise ValueError("exercise_id must not be empty")
        if self.sets is None:
            raise ValueError("sets must not be None")


