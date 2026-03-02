from dataclasses import dataclass

@dataclass(frozen=True)
class WorkoutSetInput:
    weight: float | None
    reps: int | None
    duration_time: float | None
    is_warmup: bool

    def _validate_non_negative_values(self) -> None:
        if self.weight is not None and self.weight < 0:
            raise ValueError("weight must not be negative")
        if self.reps is not None and self.reps <= 0:
            raise ValueError("reps must not be positve")
        if self.duration_time is not None and self.duration_time <= 0:
            raise ValueError("duration time must not be positive")
        
    def _validate_rep_or_duration_rule(self) -> None:
        rep_based = self.reps is not None and self.duration_time is None
        duration_based = self.reps is None and self.duration_time is not None
        if not (rep_based or duration_based):
            raise ValueError("Either duration or reps must be set. But not both.")

    def __post_init__(self) -> None:
        self._validate_non_negative_values()
        self._validate_rep_or_duration_rule()