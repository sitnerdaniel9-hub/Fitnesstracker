from application.workout import get_workout
from repository.workout_exercise_repository import WorkoutExerciseRepository
from sqlalchemy.orm import Session
from models.workout_set import WorkoutSet
from application.inputs.analysis_inputs import WeightData, RepData, TimeData

#Liefert die Personal Best für eine Übung.
#Bei Wiederholungsübungen: Das Set mit dem höchsten gewicht. Wenn es Sets mit dem gleichem Gewicht gibt, gewinnt das mit der höchsten Wiederholungsanzahl.
#Bei Zeitübungen: Das Set mit dem höchsten Gewicht. Wenn es Sets mit dem gleichem Gewicht gibt, gewinnt das mit der höchsten Zeit.

def get_pr_for_exercise(session: Session, exercise_id: int) -> WorkoutSet | None:
    repo = WorkoutExerciseRepository(session)
    return repo.find_pr_set_for_exercise(exercise_id)


#Liefert die Durschnittliche Gewichtssteigerung für eine Übung in einem Zeitraum. Nur Arbeitssätze werden berücksichtigt. Es wird immer das maximale Gewicht in einem Workout berücksichtigt.
def get_avg_weight_gain(
    weight_data: list[WeightData],
) -> float | None:
    if len(weight_data) < 2:
        return None
    weight_data.sort()
    weights = [data.weight for data in weight_data]

    diff_sum = 0.0
    for i in range(len(weights) - 1):
        diff_sum += weights[i + 1] - weights[i]

    return diff_sum / (len(weights) - 1)

def normalize_weight(w: float) -> float:
    return round(w / 0.125) * 0.125

#Liefert die Durchschnittliche Wiederholungssteigerung für eine Übung für eine Gewichtsklasse. Es wird immer die Maximale Wiedeholungsanzahl in einem Workout berücksichtigt.
def get_avg_rep_increase(rep_data: list[RepData]) -> float | None:
    if len(rep_data) < 2:
        return None
    rep_data.sort()
    rep_list = [data.reps for data in rep_data]
    diff_sum = 0.0
    for i in range(len(rep_list) - 1):
        diff_sum += rep_list[i + 1] - rep_list[i]

    return diff_sum / (len(rep_list) - 1)

#Liefert die Durchschnittliche Zeitsteigerung für eine Übung für eine Gewichtsklasse. Es wird immer die Maximale Zeit in einem Workout berücksichtigt.

def get_avg_time_increase(
    time_data: list[TimeData],
) -> float | None:
    if len(time_data) < 2:
        return None

    time_data.sort()

    duration_list = [data.duration_time for data in time_data]

    diff_sum = 0.0
    for i in range(len(duration_list) - 1):
        diff_sum += duration_list[i + 1] - duration_list[i]

    return diff_sum / (len(duration_list) - 1)

def get_plan_exercise_coverage_for_workout(session: Session, workout_id: int) -> tuple[int, int]:
    workout = get_workout(session, workout_id)
    if workout.training_plan_id is None:
        raise ValueError(f"Workout {workout_id} has no training plan assigned")

    plan_exercises = workout.training_plan.plan_exercises
    if not plan_exercises:
        return 0, 0

    logged_ids = {
        we.plan_exercise_id
        for we in workout.workout_exercises
        if we.plan_exercise_id is not None and len(we.sets) > 0
    }
    covered = sum(1 for pe in plan_exercises if pe.id in logged_ids)
    return covered, len(plan_exercises)


    
