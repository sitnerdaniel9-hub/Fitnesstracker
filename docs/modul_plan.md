application.training_plan

- Stellt Funktionen zum Erstellen, Bearbeiten und Löschen von Trainingsplänen bereit.
- Benötigt: TrainingPlanReposotory mit folgenden Operationen(create, get_by_id, get_all, update, insert, delete, find_by_name)
#Erstellt einen Trainingsplan und gibt eine TrainingPlanEntity zurück. Reihenfolge entsteht aus der Listenreihenfolge
create_training_plan(name, plan_exercises: list[PlanExerciseInput]) -> TrainingPlan

#Erstellt einen PlanExerciseInput und gibt PlanExerciseInput zurück
create_plan_exercise_input(name, target_weight: float | None, min_target_reps: int | None, max_target_reps: int | None, min_duration_time: float | None, max_duration_time: float | None, rest_sec: float | None) -> PlanExerciseInput

#Fügt einen PlanExerciseInput am Ende eines Trainingsplans ein.
add_plan_exercise(training_plan_id: int, exercise: PlanExerciseInput) -> TrainingPlan

#Löscht eine PlanExercise aus einem Trainingsplan
remove_plan_exercise(training_plan_id: int, plan_exercise_id: int) -> TrainingPlan

#Liefert den gewählten Trainingsplan
get_training_plan_by_id(training_plan_id: int) -> TrainingPlan

#Liefert alle Trainingspläne
get_all_training_plans() -> list[TrainingPlan]

#Ändert eine Übung im Trainingsplan
update_plan_exercise(training_plan_id: int, plan_exercise_id: int, plan_exercise: PlanExerciseInput) -> TrainingPlan

#Ändert den Namen eines Trainingsplans
rename_training_plan(training_plan_id: int, new_name: str) -> TrainingPlan

#Ändert den Status des TrainingsPlans
toggle_training_plan_status(training_plan_id : int) -> TrainingPlan

#Setzt eine Übung im TrainingsPlan auf eine andere Position
reorder_plan_exercises(training_plan_id: int, plan_exercise_id: int, new_position: int) -> TrainingPlan

#Gibt alle Trainingspläne zurück, dessen name den Suchstring enthält
find_training_plans_by_name(search: str) -> list[TrainingPlan]



application.workout

- Stellt Funktionen zum Erstellen, Bearbeiten und Löschen von Workouts bereit
- Benötigt:  TrainingPlanReposotory und WorkoutRepository mit folgenden Operationen(create, get_by_id, find_by_date, get_all, update, delete, find_by_name, find_by_training_plan_id)

#Erstellt ein Workout und referenziert es falls gewollt zu einem Trainingsplan
create_workout(name: str, training_plan_id: int | None, started_at: datetime | None) -> Workout

#Erstellt ein WorkoutExerciseInput
create_workout_exercise_input(name: str, working_sets: list[WorkingSetInput] | None) -> WorkoutExerciseInput

#Erstellt ein WorkingSetInput
create_working_set_input(weight: float | None, reps: int | None, duration_time: float | None) -> WorkingSetInput

#Ruft ein Workout ab
get_workout(workout_id: int) -> Workout

#Liefert alle Workouts
get_workouts() -> list[Workout]

#Liefert alle Workouts, die zu einem bestimmten Trainingsplan gehören
get_workouts_by_training_plan(training_plan_id: int) -> list[Workout]

#Liefert alle Workouts, die einen bestimmten Suchstring enthalten
get_workouts_by_name(search: str) -> list[Workout]

#Liefert alle Workouts, die nach einem bestimmten Datum gestartet wurden
get_workouts_by_date(date_ref : Date) -> list[Workout]

#Löscht ein Workout. Gibt alle verbliebenden Workouts zurück.
remove_workout(workout_id: int) -> bool

#Löscht alle Workouts nach, die vor einem Datum durchgeführt wurden. Gibt alle verbliebenden Workouts zurück.
remove_workouts_by_date(date_ref: Date) -> bool

#Fügt eine WorkoutExercise zu einem Workout hinzu
add_workout_exercise(workout_id: int, workout_exercise: WorkoutExerciseInput) -> Workout

#Verändert eine WorkoutExercise in einem Workout
update_workout_exercise(workout_id, workout_exercise_id, workout_exercise: WorkoutExerciseInput) -> Workout

#Löscht eine WorkoutExercise aus einem Workout
remove_workout_exercise(workout_id, workout_exercise_id) -> Workout

#Fügt einer WorkoutExercise in einem Workout einen Satz hinzu
add_workout_set(workout_id, workout_exercise_id, working_set: WorkingSetInput) -> Workout

#Verändert einen Satz in einer WorkoutExercise in einem Workout
update_workout_set(workout_id, workout_exercise_id, working_set_id: int, working_set: WorkingSetInput) -> Workout

#Löscht einen Satz aus einer WorkoutExercise in einem Workout
remove_workout_set(workout_id, workout_exercise_id, working_set_id: int) -> Workout

#Speichert ein Workout als Trainingsplan
save_as_training_plan(workout_id: int) -> TrainingPlan

#Schließt ein laufendes Workout ab
end_workout(workout_id: int)