from datetime import date as date_type

from pydantic import BaseModel, Field


class GoalBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    target_amount: float = Field(..., gt=0)
    due_date: date_type | None = None
    icon: str = Field("🎯", min_length=1, max_length=16)


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=80)
    target_amount: float | None = Field(None, gt=0)
    due_date: date_type | None = None
    icon: str | None = Field(None, min_length=1, max_length=16)
    clear_due_date: bool = False


class GoalContribute(BaseModel):
    amount: float = Field(..., gt=0)


class GoalOut(GoalBase):
    model_config = {"from_attributes": True}

    id: int
    current_amount: float
