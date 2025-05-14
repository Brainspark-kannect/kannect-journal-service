# app/services/journal.py
from sqlalchemy.orm import Session
from app.models.journal import JournalEntry
from app.schemas.journal import JournalEntryCreate, JournalEntryUpdate
from app.utils.nlp import analyze_sentiment
from typing import List, Optional
import logging
import traceback

logger = logging.getLogger(__name__)

def create_journal_entry(db: Session, user_id: int, entry: JournalEntryCreate) -> JournalEntry:
    """Create a new journal entry with sentiment analysis"""
    try:
        logger.info(f"Creating new journal entry for user {user_id}")
        
        # Analyze sentiment
        try:
            sentiment = analyze_sentiment(entry.content)
            logger.debug(f"Sentiment analysis result: {sentiment}")
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            raise
        
        # Create journal entry
        db_entry = JournalEntry(
            user_id=user_id,
            content=entry.content,
            sentiment_score=sentiment["score"],
            sentiment_label=sentiment["label"]
        )
        
        try:
            db.add(db_entry)
            db.commit()
            db.refresh(db_entry)
            logger.info(f"Successfully created journal entry {db_entry.id}")
            return db_entry
        except Exception as e:
            db.rollback()
            logger.error(f"Database error while creating journal entry: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            raise
            
    except Exception as e:
        logger.error(f"Failed to create journal entry: {str(e)}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        raise

def get_journal_entries(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[JournalEntry]:
    """Get all journal entries for a user"""
    try:
        logger.info(f"Fetching journal entries for user {user_id} (skip={skip}, limit={limit})")
        entries = db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id
        ).order_by(
            JournalEntry.created_at.desc()
        ).offset(skip).limit(limit).all()
        logger.info(f"Found {len(entries)} journal entries")
        return entries
    except Exception as e:
        logger.error(f"Failed to fetch journal entries: {str(e)}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        raise

def get_journal_entry(db: Session, entry_id: int, user_id: int) -> Optional[JournalEntry]:
    """Get a specific journal entry"""
    try:
        logger.info(f"Fetching journal entry {entry_id} for user {user_id}")
        entry = db.query(JournalEntry).filter(
            JournalEntry.id == entry_id,
            JournalEntry.user_id == user_id
        ).first()
        if entry:
            logger.info("Journal entry found")
        else:
            logger.info("Journal entry not found")
        return entry
    except Exception as e:
        logger.error(f"Failed to fetch journal entry: {str(e)}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        raise

def update_journal_entry(db: Session, entry: JournalEntry, entry_update: JournalEntryUpdate) -> JournalEntry:
    """Update a journal entry and recalculate sentiment"""
    try:
        logger.info(f"Updating journal entry {entry.id}")
        entry.content = entry_update.content
        
        # Re-analyze sentiment if content changed
        try:
            sentiment = analyze_sentiment(entry.content)
            entry.sentiment_score = sentiment["score"]
            entry.sentiment_label = sentiment["label"]
            logger.debug(f"Updated sentiment analysis: {sentiment}")
        except Exception as e:
            logger.error(f"Failed to update sentiment analysis: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            raise
        
        try:
            db.commit()
            db.refresh(entry)
            logger.info(f"Successfully updated journal entry {entry.id}")
            return entry
        except Exception as e:
            db.rollback()
            logger.error(f"Database error while updating journal entry: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            raise
            
    except Exception as e:
        logger.error(f"Failed to update journal entry: {str(e)}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        raise

def delete_journal_entry(db: Session, entry: JournalEntry) -> None:
    """Delete a journal entry"""
    try:
        logger.info(f"Deleting journal entry {entry.id}")
        db.delete(entry)
        db.commit()
        logger.info("Journal entry deleted successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete journal entry: {str(e)}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        raise
