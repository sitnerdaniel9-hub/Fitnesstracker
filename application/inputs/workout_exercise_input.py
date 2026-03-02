from dataclasses import dataclass
from application.inputs.workout_set_input import WorkoutSetInput

@dataclass(frozen=True)
class WorkoutExerciseInput:
    name: str
    sets: list[WorkoutSetInput]

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("name must not be empty")
        if self.sets is None:
            raise ValueError("sets must not be None")


