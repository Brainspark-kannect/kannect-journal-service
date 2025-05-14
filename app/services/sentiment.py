# app/services/sentiment.py
from app.utils.nlp import analyze_sentiment, extract_keywords
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, List
from app.models.journal import JournalEntry

def get_sentiment_summary(db: Session, user_id: int, days: int = 30) -> Dict:
    """Get sentiment analysis summary for a time period"""
    start_date = datetime.utcnow() - timedelta(days=days)
    entries = db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
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
    
    # Extract common topics or keywords
    all_content = " ".join([entry.content for entry in entries])
    keywords = extract_keywords(all_content, top_n=10)
    
    return {
        "total_entries": len(entries),
        "average_sentiment": avg_score,
        "sentiment_distribution": sentiment_counts,
        "trend": trend,
        "common_topics": keywords
    }

def analyze_entry_sentiment(text: str) -> Dict:
    """Analyze the sentiment of a journal entry"""
    return analyze_sentiment(text)
