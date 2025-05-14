# app/schemas/journal.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class JournalEntryBase(BaseModel):
    content: str

class JournalEntryCreate(JournalEntryBase):
    pass

class JournalEntryUpdate(JournalEntryBase):
    pass

class JournalEntryInDBBase(JournalEntryBase):
    id: int
    user_id: int
    sentiment_score: float
    sentiment_label: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class JournalEntry(JournalEntryInDBBase):
    pass
