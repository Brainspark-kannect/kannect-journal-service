# app/services/goal.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.goal import Goal
from app.schemas.goal import GoalCreate, GoalUpdate

def create_goal(db: Session, user_id: int, goal: GoalCreate) -> Goal:
    """Create a new goal"""
    db_goal = Goal(
        user_id=user_id,
        title=goal.title,
        description=goal.description,
        due_date=goal.due_date,
        status=goal.status
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

def get_goals(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Goal]:
    """Get all goals for a user"""
    return db.query(Goal).filter(Goal.user_id == user_id).offset(skip).limit(limit).all()

def get_goal(db: Session, goal_id: int, user_id: int) -> Optional[Goal]:
    """Get a specific goal"""
    return db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()

def update_goal(db: Session, goal: Goal, goal_update: GoalUpdate) -> Goal:
    """Update a goal"""
    for key, value in goal_update.dict(exclude_unset=True).items():
        setattr(goal, key, value)
    
    db.commit()
    db.refresh(goal)
    return goal

def delete_goal(db: Session, goal: Goal) -> None:
    """Delete a goal"""
    db.delete(goal)
    db.commit()
