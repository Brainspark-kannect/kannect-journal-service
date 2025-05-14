# app/api/habits.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timedelta
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.habit import Habit, HabitLog
from app.schemas.habit import Habit as HabitSchema, HabitCreate, HabitUpdate, HabitLog as HabitLogSchema, HabitLogCreate
from app.services.habit import create_habit, get_habits, get_habit, update_habit, delete_habit, log_habit_completion, get_habit_logs
from app.config.settings import settings

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/habits",
    tags=["Habits"],
)

@router.post("/", response_model=HabitSchema)
async def add_habit(
    habit: HabitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new habit"""
    return create_habit(db, current_user.id, habit)

@router.get("/", response_model=List[HabitSchema])
async def read_habits(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all habits"""
    return get_habits(db, current_user.id, skip, limit)

@router.get("/stats", response_model=Dict)
async def get_habit_stats(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get habit statistics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get user's habits
    habits = get_habits(db, current_user.id)
    
    if not habits:
        return {"message": "No habits found"}
    
    habit_stats = {}
    
    for habit in habits:
        # Get logs for this habit
        logs = get_habit_logs(db, habit.id, start_date)
        
        # Calculate streak and completion rate
        total_days = days
        completion_days = len(set(log.completed_at.date() for log in logs))
        
        # Calculate current streak
        current_streak = 0
        date_check = datetime.utcnow().date()
        
        while True:
            completion_on_date = any(log.completed_at.date() == date_check for log in logs)
            if not completion_on_date:
                break
            current_streak += 1
            date_check -= timedelta(days=1)
        
        habit_stats[habit.id] = {
            "name": habit.name,
            "total_completions": len(logs),
            "completion_rate": completion_days / total_days if total_days > 0 else 0,
            "current_streak": current_streak
        }
    
    return {
        "period_days": days,
        "habit_stats": habit_stats
    }

@router.get("/{habit_id}", response_model=HabitSchema)
async def read_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific habit"""
    habit = get_habit(db, habit_id, current_user.id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    return habit

@router.put("/{habit_id}", response_model=HabitSchema)
async def update_habit_route(
    habit_id: int,
    habit_update: HabitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a habit"""
    habit = get_habit(db, habit_id, current_user.id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    return update_habit(db, habit, habit_update)

@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit_route(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a habit"""
    habit = get_habit(db, habit_id, current_user.id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    delete_habit(db, habit)
    return None

@router.post("/log", response_model=HabitLogSchema)
async def log_habit(
    log: HabitLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log a habit completion"""
    habit = get_habit(db, log.habit_id, current_user.id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    return log_habit_completion(db, log)

@router.get("/log/{habit_id}", response_model=List[HabitLogSchema])
async def get_habit_logs_route(
    habit_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get habit logs for a specific habit"""
    habit = get_habit(db, habit_id, current_user.id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    start_date = datetime.utcnow() - timedelta(days=days)
    return get_habit_logs(db, habit_id, start_date)
