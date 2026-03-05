from application.workout import get_workouts_by_date
from application.workout import get_workouts
from sqlalchemy.orm import Session
from datetime import datetime
from models.workout import Workout
from models.workout_set import WorkoutSet

def count_workouts_in_date_range(session: Session, start: datetime, end: datetime) -> int:
    return len(get_workouts_by_date(session, start, end))    

def _get_relevant_datetime(workout: Workout) -> datetime | None:
    return workout.completed_at if workout.completed_at is not None else workout.started_at

def _calc_avg(workout_count: int, start: datetime, end: datetime) -> float:
    if workout_count == 0:
        return 0.0

    if start > end:
        raise ValueError("start must be less than or equal to end")

    days = (end.date() - start.date()).days + 1
    weeks = days / 7.0

    return workout_count / weeks


def _count_avg_workouts_per_week_at_start(session: Session, start: datetime) -> float:
    end = datetime.now()
    workouts = get_workouts_by_date(session, start, end)
    return _calc_avg(len(workouts), start, end)


def _count_avg_workouts_per_week_to_end(session: Session, end: datetime) -> float:
    workouts = get_workouts(session)
    filtered_workouts: list[Workout] = []

    for workout in workouts:
        dt = _get_relevant_datetime(workout)
        if dt is not None and dt < end:
            filtered_workouts.append(workout)

    if not filtered_workouts:
        return 0.0

    dates = [_get_relevant_datetime(workout) for workout in filtered_workouts]
    dates = [dt for dt in dates if dt is not None]

    start = min(dates)
    return _calc_avg(len(filtered_workouts), start, end)


def _count_avg_workouts_per_week_from_start_to_end(
    session: Session,
    start: datetime,
    end: datetime,
) -> float:
    workouts = get_workouts_by_date(session, start, end)
    return _calc_avg(len(workouts), start, end)


def _count_avg_workouts_per_week_full_range(session: Session) -> float:
    workouts = get_workouts(session)
    if not workouts:
        return 0.0

    dates = [_get_relevant_datetime(workout) for workout in workouts]
    dates = [dt for dt in dates if dt is not None]

    if not dates:
        return 0.0

    start = min(dates)
    end = max(dates)

    return _calc_avg(len(workouts), start, end)


def count_avg_workouts_per_week(
    session: Session,
    start: datetime | None = None,
    end: datetime | None = None,
) -> float:
    if start is not None and end is not None and start > end:
        raise ValueError("start must be less than or equal to end")

    if start is not None and end is None:
        return _count_avg_workouts_per_week_at_start(session, start)

    if start is None and end is not None:
        return _count_avg_workouts_per_week_to_end(session, end)

    if start is not None and end is not None:
        return _count_avg_workouts_per_week_from_start_to_end(session, start, end)

    return _count_avg_workouts_per_week_full_range(session)

#Liefert die Personal Best für eine Übung.
#Bei Wiederholungsübungen: Das Set mit dem höchsten gewicht. Wenn es Sets mit dem gleichem Gewicht gibt, gewinnt das mit der höchsten Wiederholungsanzahl.
#Bei Zeitübungen: Das Set mit dem höchsten Gewicht. Wenn es Sets mit dem gleichem Gewicht gibt, gewinnt das mit der höchsten Zeit.

def get_pr_for_exercise(session: Session, plan_exercise_id: int) -> WorkoutSet | None:
    best: WorkoutSet | None = None

    def score(s: WorkoutSet) -> tuple[float, float]:
        weight = s.weight if s.weight is not None else -1.0
        # Tie-breaker: nimm reps, wenn vorhanden, sonst duration_time, sonst -1
        tie = (
            float(s.reps) if s.reps is not None
            else float(s.duration_time) if s.duration_time is not None
            else -1.0
        )
        return (weight, tie)

    workouts = get_workouts(session)
    for workout in workouts:
        for ex in workout.workout_exercises:
            if ex.plan_exercise_id != plan_exercise_id:
                continue

            for s in ex.sets:
                if s.isWarmup:
                    continue

                if best is None or score(s) > score(best):
                    best = s

    return best


#Liefert die Durschnittliche Gewichtssteigerung für eine Übung in einem Zeitraum. Nur Arbeitssätze werden berücksichtigt. Es wird immer das maximale Gewicht in einem Workout berücksichtigt.
def get_avg_weight_gain(
    session: Session,
    plan_exercise_id: int,
    start: datetime | None = None,
    end: datetime | None = None,
) -> float | None:
    if start is None:
        start = datetime.min
    if end is None:
        end = datetime.max

    workouts = get_workouts_by_date(session, start, end)

    points: list[tuple[datetime, float]] = []
    for workout in workouts:
        if workout.completed_at is None:
            continue

        for ex in workout.workout_exercises:
            if ex.plan_exercise_id != plan_exercise_id:
                continue

            max_weight: float | None = None
            for s in ex.sets:
                if s.isWarmup:
                    continue
                if s.weight is None:
                    continue
                if max_weight is None or s.weight > max_weight:
                    max_weight = s.weight

            if max_weight is not None:
                points.append((workout.completed_at, max_weight))

    if len(points) < 2:
        return None

    points.sort(key=lambda p: p[0])
    weights = [w for _, w in points]

    diff_sum = 0.0
    for i in range(len(weights) - 1):
        diff_sum += weights[i + 1] - weights[i]

    return diff_sum / (len(weights) - 1)




def normalize_weight(w: float) -> float:
    return round(w / 0.125) * 0.125

#Liefert die Durchschnittliche Wiederholungssteigerung für eine Übung für eine Gewichtsklasse. Es wird immer die Maximale Wiedeholungsanzahl in einem Workout berücksichtigt.
def get_avg_rep_increase(session: Session, plan_exercise_id: int, weight: float | None) -> float | None:
    workouts = get_workouts(session)
    points: list[tuple[datetime, int]] = []
    for workout in workouts:
        if workout.completed_at is None:
            continue
        best_reps_in_workout: int | None = None
        for ex in workout.workout_exercises:
            if ex.plan_exercise_id != plan_exercise_id:
                continue
        
            for s in ex.sets:
                if s.isWarmup:
                    continue
                if s.reps is None:
                    continue

                if weight is None:
                    if s.weight is not None:
                        continue
                else:
                    if s.weight is None:
                        continue
                    if normalize_weight(s.weight) != normalize_weight(weight):
                        continue

                if best_reps_in_workout is None or s.reps > best_reps_in_workout:
                    best_reps_in_workout = s.reps
        if best_reps_in_workout is not None:
            points.append((workout.completed_at, best_reps_in_workout))
        
    if len(points) < 2:
        return None
    points.sort(key=lambda p: p[0])
    rep_list = [w for _, w in points]
    diff_sum = 0.0
    for i in range(len(rep_list) - 1):
        diff_sum += rep_list[i + 1] - rep_list[i]

    return diff_sum / (len(rep_list) - 1)

#Liefert die Durchschnittliche Zeitsteigerung für eine Übung für eine Gewichtsklasse. Es wird immer die Maximale Zeit in einem Workout berücksichtigt.

def get_avg_time_increase(session: Session, plan_exercise_id: int, weight: float| None) -> float | None:
    workouts = get_workouts(session)
    points: list[tuple[datetime, float]] = []
    for workout in workouts:
        if workout.completed_at is None:
            continue
        best_duration_in_workout: float | None = None
        for ex in workout.workout_exercises:
            if ex.plan_exercise_id != plan_exercise_id:
                continue
        
            for s in ex.sets:
                if s.isWarmup:
                    continue
                if s.duration_time is None:
                    continue

                if weight is None:
                    if s.weight is not None:
                        continue
                else:
                    if s.weight is None:
                        continue
                    if normalize_weight(s.weight) != normalize_weight(weight):
                        continue

                if best_duration_in_workout is None or s.duration_time > best_duration_in_workout:
                    best_duration_in_workout = s.duration_time
        if best_duration_in_workout is not None:
            points.append((workout.completed_at, best_duration_in_workout))
        
    if len(points) < 2:
        return None
    points.sort(key=lambda p: p[0])
    duration_list = [w for _, w in points]
    diff_sum = 0.0
    for i in range(len(duration_list) - 1):
        diff_sum += duration_list[i + 1] - duration_list[i]

    return diff_sum / (len(duration_list) - 1)

    
