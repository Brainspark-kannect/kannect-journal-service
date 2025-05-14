# app/schemas/goal.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: datetime = Field(..., alias="target_date")
    status: str = "not-started"  # not-started, in-progress, completed

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "Learn Python",
                "description": "Master Python programming",
                "target_date": "2024-12-31",
                "status": "not-started"
            }
        }

class GoalCreate(GoalBase):
    pass

class GoalUpdate(GoalBase):
    pass

class GoalInDBBase(GoalBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class Goal(GoalInDBBase):
    pass
