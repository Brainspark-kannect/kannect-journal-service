# app/services/habit.py
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.models.habit import Habit, HabitLog
from app.schemas.habit import HabitCreate, HabitUpdate, HabitLogCreate

def create_habit(db: Session, user_id: int, habit: HabitCreate) -> Habit:
    """Create a new habit"""
    db_habit = Habit(
        user_id=user_id,
        name=habit.name,
        description=habit.description,
        frequency=habit.frequency
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit

def get_habits(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Habit]:
    """Get all habits for a user"""
    return db.query(Habit).filter(Habit.user_id == user_id).offset(skip).limit(limit).all()

def get_habit(db: Session, habit_id: int, user_id: int) -> Optional[Habit]:
    """Get a specific habit"""
    return db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user_id).first()

def update_habit(db: Session, habit: Habit, habit_update: HabitUpdate) -> Habit:
    """Update a habit"""
    for key, value in habit_update.dict(exclude_unset=True).items():
        setattr(habit, key, value)
    
    db.commit()
    db.refresh(habit)
    return habit

def delete_habit(db: Session, habit: Habit) -> None:
    """Delete a habit"""
    db.delete(habit)
    db.commit()

def log_habit_completion(db: Session, log: HabitLogCreate) -> HabitLog:
    """Log a habit completion"""
    db_log = HabitLog(
        habit_id=log.habit_id,
        notes=log.notes
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_habit_logs(db: Session, habit_id: int, start_date: datetime) -> List[HabitLog]:
    """Get logs for a specific habit after a given date"""
    return db.query(HabitLog).filter(
        HabitLog.habit_id == habit_id,
        HabitLog.completed_at >= start_date
    ).order_by(HabitLog.completed_at.desc()).all()
