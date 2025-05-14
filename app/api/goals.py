# app/api/goals.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.goal import Goal, GoalCreate, GoalUpdate
from app.services.goal import create_goal, get_goals, get_goal, update_goal, delete_goal
from app.config.settings import settings

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/goals",
    tags=["Goals"],
)

@router.post("/", response_model=Goal)
async def add_goal(
    goal: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new goal"""
    return create_goal(db, current_user.id, goal)

@router.get("/", response_model=List[Goal])
async def read_goals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all goals"""
    return get_goals(db, current_user.id, skip, limit)

@router.get("/{goal_id}", response_model=Goal)
async def read_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific goal"""
    goal = get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    return goal

@router.put("/{goal_id}", response_model=Goal)
async def update_goal_route(
    goal_id: int,
    goal_update: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a goal"""
    goal = get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    return update_goal(db, goal, goal_update)

@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal_route(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a goal"""
    goal = get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    delete_goal(db, goal)
    return None
