# app/api/dashboard.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List
from datetime import datetime, timedelta
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.journal import JournalEntry
from app.models.habit import Habit, HabitLog
from app.models.goal import Goal
from app.services.journal import get_journal_entries
from app.services.habit import get_habits, get_habit_logs
from app.services.goal import get_goals
from app.config.settings import settings

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/dashboard",
    tags=["Dashboard"],
)

@router.get("/stats", response_model=Dict)
async def get_dashboard_stats(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get combined stats for dashboard"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get journal entries
    journal_entries = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user.id,
        JournalEntry.created_at >= start_date
    ).all()
    
    # Get habits and their logs
    habits = db.query(Habit).filter(Habit.user_id == current_user.id).all()
    habit_ids = [h.id for h in habits]
    habit_logs = db.query(HabitLog).filter(
        HabitLog.habit_id.in_(habit_ids),
        HabitLog.completed_at >= start_date
    ).all()
    
    # Get goals
    goals = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.created_at >= start_date
    ).all()
    
    # Calculate stats
    
    # Journal sentiment stats
    avg_sentiment = sum(entry.sentiment_score for entry in journal_entries) / len(journal_entries) if journal_entries else 0
    sentiment_counts = {
        "positive": len([e for e in journal_entries if e.sentiment_label == "positive"]),
        "neutral": len([e for e in journal_entries if e.sentiment_label == "neutral"]),
        "negative": len([e for e in journal_entries if e.sentiment_label == "negative"])
    }
    
    # Habit completion stats
    habit_stats = {}
    for habit in habits:
        completions = [log for log in habit_logs if log.habit_id == habit.id]
        habit_stats[habit.name] = len(completions)
    
    # Goal stats
    goal_status_counts = {
        "not-started": len([g for g in goals if g.status == "not-started"]),
        "in-progress": len([g for g in goals if g.status == "in-progress"]),
        "completed": len([g for g in goals if g.status == "completed"])
    }
    
    # Find correlations between sentiment and habits
    correlations = []
    if journal_entries and habit_logs:
        # Group entries by date
        entries_by_date = {}
        for entry in journal_entries:
            date = entry.created_at.date()
            if date not in entries_by_date:
                entries_by_date[date] = []
            entries_by_date[date].append(entry)
        
        # Group habit logs by date
        logs_by_date = {}
        for log in habit_logs:
            date = log.completed_at.date()
            if date not in logs_by_date:
                logs_by_date[date] = []
            logs_by_date[date].append(log)
        
        # Find dates with both entries and habit logs
        common_dates = set(entries_by_date.keys()) & set(logs_by_date.keys())
        
        # Calculate average sentiment for each date
        date_sentiments = {}
        for date in common_dates:
            date_entries = entries_by_date[date]
            avg_sent = sum(e.sentiment_score for e in date_entries) / len(date_entries)
            date_sentiments[date] = avg_sent
        
        # Check if completing habits correlates with better sentiment
        for habit in habits:
            habit_completion_dates = [date for date in common_dates if any(log.habit_id == habit.id for log in logs_by_date[date])]
            non_completion_dates = common_dates - set(habit_completion_dates)
            
            if habit_completion_dates and non_completion_dates:
                avg_sentiment_with_habit = sum(date_sentiments[date] for date in habit_completion_dates) / len(habit_completion_dates)
                avg_sentiment_without_habit = sum(date_sentiments[date] for date in non_completion_dates) / len(non_completion_dates)
                
                correlations.append({
                    "habit": habit.name,
                    "avg_sentiment_with_habit": avg_sentiment_with_habit,
                    "avg_sentiment_without_habit": avg_sentiment_without_habit,
                    "difference": avg_sentiment_with_habit - avg_sentiment_without_habit
                })
    
    return {
        "period_days": days,
        "journal_stats": {
            "total_entries": len(journal_entries),
            "average_sentiment": avg_sentiment,
            "sentiment_distribution": sentiment_counts
        },
        "habit_stats": habit_stats,
        "goal_stats": goal_status_counts,
        "correlations": correlations
    }

@router.get("/sentiment/summary")
async def get_sentiment_summary(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sentiment analysis summary"""
    start_date = datetime.utcnow() - timedelta(days=days)
    entries = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user.id,
        JournalEntry.created_at >= start_date
    ).all()
    
    if not entries:
        return {"message": "No entries found for the specified time period"}
    
    # Calculate averages and trends
    total_score = sum(entry.sentiment_score for entry in entries)
    avg_score = total_score / len(entries)
    
    # Count sentiment labels
    sentiment_counts = {
        "positive": len([e for e in entries if e.sentiment_label == "positive"]),
        "neutral": len([e for e in entries if e.sentiment_label == "neutral"]),
        "negative": len([e for e in entries if e.sentiment_label == "negative"])
    }
    
    # Get trend (improving, stable, declining)
    if len(entries) >= 2:
        # Sort entries by date
        sorted_entries = sorted(entries, key=lambda x: x.created_at)
        # Calculate trend using simple comparison
        first_half = sorted_entries[:len(sorted_entries)//2]
        second_half = sorted_entries[len(sorted_entries)//2:]
        
        first_half_avg = sum(e.sentiment_score for e in first_half) / len(first_half)
        second_half_avg = sum(e.sentiment_score for e in second_half) / len(second_half)
        
        if second_half_avg > first_half_avg + 0.1:
            trend = "improving"
        elif second_half_avg < first_half_avg - 0.1:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "not enough data"
    
    return {
        "total_entries": len(entries),
        "average_sentiment": avg_score,
        "sentiment_distribution": sentiment_counts,
        "trend": trend
    }
