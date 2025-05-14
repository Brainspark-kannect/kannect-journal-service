# app/services/stats.py
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, List
from app.models.journal import JournalEntry
from app.models.habit import Habit, HabitLog
from app.models.goal import Goal
from app.services.sentiment import get_sentiment_summary

def get_dashboard_stats(db: Session, user_id: int, days: int = 30) -> Dict:
    """Get combined stats for dashboard"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get journal entries
    journal_entries = db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.created_at >= start_date
    ).all()
    
    # Get habits and their logs
    habits = db.query(Habit).filter(Habit.user_id == user_id).all()
    habit_ids = [h.id for h in habits]
    habit_logs = db.query(HabitLog).filter(
        HabitLog.habit_id.in_(habit_ids),
        HabitLog.completed_at >= start_date
    ).all()
    
    # Get goals
    goals = db.query(Goal).filter(
        Goal.user_id == user_id,
        Goal.created_at >= start_date
    ).all()
    
    # Get sentiment summary
    sentiment_summary = get_sentiment_summary(db, user_id, days)
    
    # Calculate habit stats
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
    correlations = find_habit_sentiment_correlations(journal_entries, habits, habit_logs)
    
    return {
        "period_days": days,
        "journal_stats": sentiment_summary,
        "habit_stats": habit_stats,
        "goal_stats": goal_status_counts,
        "correlations": correlations
    }

def find_habit_sentiment_correlations(journal_entries: List[JournalEntry], habits: List[Habit], habit_logs: List[HabitLog]) -> List[Dict]:
    """Find correlations between habits and sentiment"""
    if not journal_entries or not habit_logs:
        return []
    
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
    correlations = []
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
    
    return correlations
