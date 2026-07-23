from dataclasses import dataclass

@dataclass(frozen=True)
class PlanExerciseInput:
    # TODO: PlanExercise hat kein eigenes `name` mehr (jetzt über Exercise-Relationship).
    # Dieses Feld muss durch eine exercise_id ersetzt/ergänzt werden.
    name: str
    targeted_weight: float | None
    min_targeted_reps: int | None
    max_targeted_reps: int | None
    min_duration_time: float | None
    max_duration_time: float | None
    rest_sec: float | None

    def _validate_name(self) -> None:
        # TODO: validiert das obsolete `name`-Feld (siehe TODO oben) statt einer Exercise-Referenz.
        if not self.name or not self.name.strip():
            raise ValueError("name must not be empty")
        
    def _validate_non_negative_values(self) -> None:
        if self.rest_sec is not None and self.rest_sec < 0:
            raise ValueError("rest_sec must be greater than or equal to 0")

        if self.targeted_weight is not None and self.targeted_weight < 0:
            raise ValueError("target_weight must be greater than or equal to 0")

        if self.min_targeted_reps is not None and self.min_targeted_reps < 0:
            raise ValueError("min_targeted_reps must be greater than or equal to 0")

        if self.max_targeted_reps is not None and self.max_targeted_reps < 0:
            raise ValueError("max_targeted_reps must be greater than or equal to 0")

        if self.min_duration_time is not None and self.min_duration_time < 0:
            raise ValueError("min_duration_time must be greater than or equal to 0")

        if self.max_duration_time is not None and self.max_duration_time < 0:
            raise ValueError("max_duration_time must be greater than or equal to 0")
    
    def _validate_rep_or_duration_rule(self) -> None:
        has_reps = self.min_targeted_reps is not None or self.max_targeted_reps is not None
        has_duration = self.min_duration_time is not None or self.max_duration_time is not None

        if not has_reps and not has_duration:
            raise ValueError(
                "Either min_targeted_reps/max_targeted_reps or "
                "min_duration_time/max_duration_time must be set"
            )
        
        if has_reps and has_duration:
            raise ValueError(
                "Repetition-based and duration-based targets cannot be set at the same time"
            )

        if has_reps:
            self._validate_reps()

        if has_duration:
            self._validate_duration()

    def _validate_reps(self) -> None:
        if self.min_targeted_reps is None or self.max_targeted_reps is None:
            raise ValueError(
                "min_targeted_reps and max_targeted_reps must both be set together"
            )

        if self.min_targeted_reps > self.max_targeted_reps:
            raise ValueError("min_targeted_reps must be <= max_targeted_reps")
        
    def _validate_duration(self) -> None:
        if self.min_duration_time is None or self.max_duration_time is None:
            raise ValueError(
                "min_duration_time and max_duration_time must both be set together"
            )

        if self.min_duration_time > self.max_duration_time:
            raise ValueError("min_duration_time must be <= max_duration_time")


    def __post_init__(self) -> None:
        self._validate_name()
        self._validate_non_negative_values()
        self._validate_rep_or_duration_rule()

        
        
        
