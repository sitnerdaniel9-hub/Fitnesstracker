from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True, order=True)
class WeightData:
    completed_at: datetime
    weight: float

@dataclass(frozen=True, order=True)
class RepData:
    completed_at: datetime
    reps: int

@dataclass(frozen=True, order=True)
class TimeData:
    completed_at: datetime
    duration_time: float
