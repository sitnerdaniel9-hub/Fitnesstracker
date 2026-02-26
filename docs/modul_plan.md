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

