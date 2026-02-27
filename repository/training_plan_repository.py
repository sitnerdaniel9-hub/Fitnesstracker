#Enthält die Persistenzoperationen für Trainingspläne. Kapselt den Datenbankzugriff (CRUD) auf TrainingPlan-Entitäten.

from sqlalchemy.orm import Session
from sqlalchemy import select
from models.training_plan import TrainingPlan

class TrainingPlanRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, training_plan: TrainingPlan) -> TrainingPlan:
        self.session.add(training_plan)
        return training_plan
    
    def find_by_id(self, training_plan_id: int) -> TrainingPlan | None:
        return self.session.get(TrainingPlan, training_plan_id)
    
    def find_all(self) -> list[TrainingPlan]:
        return self.session.scalars(select(TrainingPlan).order_by(TrainingPlan.id)).all()
    
    def find_by_name(self, search: str) -> list[TrainingPlan]:
        stmt = select(TrainingPlan).where(
            TrainingPlan.name.ilike(f"%{search}%")
        ).order_by(TrainingPlan.id)
        return self.session.scalars(stmt).all()
    
    def update(self, training_plan: TrainingPlan) -> TrainingPlan:
        return training_plan
    
    def delete(self, training_plan: TrainingPlan) -> None:
        self.session.delete(training_plan)
    


    

    
