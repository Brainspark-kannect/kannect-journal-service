# app/schemas/habit.py
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None
    frequency: str

class HabitCreate(HabitBase):
    pass

class HabitUpdate(HabitBase):
    pass

class HabitInDBBase(HabitBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class Habit(HabitInDBBase):
    pass

class HabitLogBase(BaseModel):
    habit_id: int
    notes: Optional[str] = None

class HabitLogCreate(HabitLogBase):
    pass

class HabitLogInDBBase(HabitLogBase):
    id: int
    completed_at: datetime
    
    class Config:
        orm_mode = True

class HabitLog(HabitLogInDBBase):
    pass
