from datetime import datetime

from pydantic import BaseModel

from api.schemas.exercise import ExerciseRead

class WorkoutRead(BaseModel):
    id: int
    name: str
    started_at: datetime
    completed_at: datetime | None
    training_plan_id: int | None

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}

class WorkoutSetRead(BaseModel):
    id: int
    workout_exercise_id: int
    weight: float | None
    reps: int | None
    duration_time: float | None
    isWarmup: bool

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}

class WorkoutExercisesRead(BaseModel):
    id: int
    exercise: ExerciseRead
    plan_exercise_id: int | None
    workout_id: int
    sets: list[WorkoutSetRead]

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}

class WorkoutReadDetailed(BaseModel):
    id: int
    name: str
    started_at: datetime
    completed_at: datetime | None
    training_plan_id: int | None
    workout_exercises: list[WorkoutExercisesRead]

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}

class CoverageRead(BaseModel):
    covered: int
    sum_of_exercises: int

class WorkoutCreateOrUpdate(BaseModel):
    name: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    training_plan_id: int | None = None

class WorkoutSetCreate(BaseModel):
    weight: float | None = None
    reps: int | None = None
    duration_time: float | None = None
    is_warmup: bool = False

class WorkoutSetCreateFromPlan(BaseModel):
    exercise_id: int
    plan_exercise_id: int
    weight: float | None = None
    reps: int | None = None
    duration_time: float | None = None
    is_warmup: bool = False

class WorkoutExerciseCreate(BaseModel):
    exercise_id: int
    plan_exercise_id: int | None = None

class WorkoutFinish(BaseModel):
    completed_at: datetime | None = None

