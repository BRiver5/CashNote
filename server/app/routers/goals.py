from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_device_id
from ..models import SavingGoal
from ..schemas.goal import GoalContribute, GoalCreate, GoalOut, GoalUpdate

router = APIRouter(prefix="/goals", tags=["goals"])


def _get_owned_goal(db: Session, device_id: str, goal_id: int) -> SavingGoal:
    goal = (
        db.query(SavingGoal)
        .filter(SavingGoal.id == goal_id, SavingGoal.device_id == device_id)
        .first()
    )
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.get("", response_model=list[GoalOut])
def list_goals(
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    return (
        db.query(SavingGoal)
        .filter(SavingGoal.device_id == device_id)
        .order_by(SavingGoal.id.asc())
        .all()
    )


@router.post("", response_model=GoalOut, status_code=201)
def create_goal(
    payload: GoalCreate,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    goal = SavingGoal(
        device_id=device_id,
        name=payload.name,
        target_amount=payload.target_amount,
        current_amount=0.0,
        due_date=payload.due_date,
        icon=payload.icon,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.put("/{goal_id}", response_model=GoalOut)
def update_goal(
    goal_id: int,
    payload: GoalUpdate,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    goal = _get_owned_goal(db, device_id, goal_id)
    if payload.name is not None:
        goal.name = payload.name
    if payload.target_amount is not None:
        goal.target_amount = payload.target_amount
    if payload.clear_due_date:
        goal.due_date = None
    elif payload.due_date is not None:
        goal.due_date = payload.due_date
    if payload.icon is not None:
        goal.icon = payload.icon
    db.commit()
    db.refresh(goal)
    return goal


@router.patch("/{goal_id}/contribute", response_model=GoalOut)
def contribute_to_goal(
    goal_id: int,
    payload: GoalContribute,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    goal = _get_owned_goal(db, device_id, goal_id)
    goal.current_amount = float(goal.current_amount) + payload.amount
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=204)
def delete_goal(
    goal_id: int,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    goal = _get_owned_goal(db, device_id, goal_id)
    db.delete(goal)
    db.commit()
