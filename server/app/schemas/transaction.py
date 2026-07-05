from datetime import date as date_type
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class TransactionBase(BaseModel):
    category_id: int
    type: Literal["income", "expense"]
    amount: float = Field(..., gt=0)
    note: str | None = Field(None, max_length=255)
    date: date_type


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    category_id: int | None = None
    type: Literal["income", "expense"] | None = None
    amount: float | None = Field(None, gt=0)
    note: str | None = Field(None, max_length=255)
    date: date_type | None = None


class TransactionOut(TransactionBase):
    model_config = {"from_attributes": True}

    id: int
    created_at: datetime
