from dataclasses import dataclass
from application.inputs.workout_set_input import WorkoutSetInput
from application.inputs.plan_exercise_input import PlanExerciseInput

@dataclass(frozen=True)
class WorkoutExerciseInput:
    # TODO: WorkoutExercise hat kein eigenes `name` mehr (jetzt über Exercise-Relationship).
    # Dieses Feld muss durch eine exercise_id ersetzt/ergänzt werden.
    name: str
    plan_exercise_id: int | None
    sets: list[WorkoutSetInput]

    def __post_init__(self):
        # TODO: validiert das obsolete `name`-Feld (siehe TODO oben) statt einer Exercise-Referenz.
        if not self.name or not self.name.strip():
            raise ValueError("name must not be empty")
        if self.sets is None:
            raise ValueError("sets must not be None")


