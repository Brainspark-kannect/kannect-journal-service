# app/api/journal.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.journal import JournalEntry, JournalEntryCreate, JournalEntryUpdate
from app.services.journal import create_journal_entry, get_journal_entries, get_journal_entry, update_journal_entry, delete_journal_entry
from app.config.settings import settings

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/journal",
    tags=["Journal"],
)

@router.post("/", response_model=JournalEntry)
async def add_journal_entry(
    entry: JournalEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a new journal entry"""
    return create_journal_entry(db, current_user.id, entry)

@router.get("/", response_model=List[JournalEntry])
async def read_journal_entries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all journal entries"""
    return get_journal_entries(db, current_user.id, skip, limit)

@router.get("/{entry_id}", response_model=JournalEntry)
async def read_journal_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific journal entry"""
    entry = get_journal_entry(db, entry_id, current_user.id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    return entry

@router.put("/{entry_id}", response_model=JournalEntry)
async def update_entry(
    entry_id: int,
    entry_update: JournalEntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a journal entry"""
    entry = get_journal_entry(db, entry_id, current_user.id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    return update_journal_entry(db, entry, entry_update)

@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a journal entry"""
    entry = get_journal_entry(db, entry_id, current_user.id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    delete_journal_entry(db, entry)
    return None
