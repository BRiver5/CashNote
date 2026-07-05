import calendar
from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_device_id
from ..models import Category, Transaction, TransactionType
from ..schemas.transaction import TransactionCreate, TransactionOut, TransactionUpdate

router = APIRouter(prefix="/transactions", tags=["transactions"])


def month_bounds(month: str) -> tuple[date, date]:
    try:
        year_str, month_str = month.split("-")
        year, month_num = int(year_str), int(month_str)
        first = date(year, month_num, 1)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=422, detail="month must be YYYY-MM")
    last = date(year, month_num, calendar.monthrange(year, month_num)[1])
    return first, last


def _get_owned_transaction(db: Session, device_id: str, tx_id: int) -> Transaction:
    tx = (
        db.query(Transaction)
        .filter(Transaction.id == tx_id, Transaction.device_id == device_id)
        .first()
    )
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


def _validate_category(db: Session, device_id: str, category_id: int) -> None:
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.device_id == device_id)
        .first()
    )
    if category is None:
        raise HTTPException(status_code=422, detail="Unknown category for this device")


@router.get("", response_model=list[TransactionOut])
def list_transactions(
    month: str | None = Query(None, description="YYYY-MM"),
    category_id: int | None = None,
    type: Literal["income", "expense"] | None = None,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    query = db.query(Transaction).filter(Transaction.device_id == device_id)
    if month is not None:
        first, last = month_bounds(month)
        query = query.filter(Transaction.date >= first, Transaction.date <= last)
    if category_id is not None:
        query = query.filter(Transaction.category_id == category_id)
    if type is not None:
        query = query.filter(Transaction.type == TransactionType(type))
    return query.order_by(Transaction.date.desc(), Transaction.created_at.desc()).all()


@router.post("", response_model=TransactionOut, status_code=201)
def create_transaction(
    payload: TransactionCreate,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    _validate_category(db, device_id, payload.category_id)
    tx = Transaction(
        device_id=device_id,
        category_id=payload.category_id,
        type=TransactionType(payload.type),
        amount=payload.amount,
        note=payload.note,
        date=payload.date,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


@router.put("/{tx_id}", response_model=TransactionOut)
def update_transaction(
    tx_id: int,
    payload: TransactionUpdate,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    tx = _get_owned_transaction(db, device_id, tx_id)
    if payload.category_id is not None:
        _validate_category(db, device_id, payload.category_id)
        tx.category_id = payload.category_id
    if payload.type is not None:
        tx.type = TransactionType(payload.type)
    if payload.amount is not None:
        tx.amount = payload.amount
    if payload.note is not None:
        tx.note = payload.note
    if payload.date is not None:
        tx.date = payload.date
    db.commit()
    db.refresh(tx)
    return tx


@router.delete("/{tx_id}", status_code=204)
def delete_transaction(
    tx_id: int,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    tx = _get_owned_transaction(db, device_id, tx_id)
    db.delete(tx)
    db.commit()
