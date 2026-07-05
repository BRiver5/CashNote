from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_device_id
from ..models import Category, Transaction, TransactionType
from ..schemas.summary import (
    CategoryBreakdownItem,
    MonthlySummary,
    TrendPoint,
    TrendSummary,
)
from .transactions import month_bounds

router = APIRouter(prefix="/summary", tags=["summary"])


def _shift_month(base: date, offset: int) -> tuple[int, int]:
    total = base.year * 12 + (base.month - 1) + offset
    return total // 12, total % 12 + 1


@router.get("/monthly", response_model=MonthlySummary)
def monthly_summary(
    month: str = Query(..., description="YYYY-MM"),
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    first, last = month_bounds(month)

    totals = dict(
        db.query(Transaction.type, func.coalesce(func.sum(Transaction.amount), 0.0))
        .filter(
            Transaction.device_id == device_id,
            Transaction.date >= first,
            Transaction.date <= last,
        )
        .group_by(Transaction.type)
        .all()
    )

    breakdown_rows = (
        db.query(
            Category.id,
            Category.name,
            Category.color,
            Category.icon,
            func.sum(Transaction.amount).label("total"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(
            Transaction.device_id == device_id,
            Transaction.type == TransactionType.expense,
            Transaction.date >= first,
            Transaction.date <= last,
        )
        .group_by(Category.id, Category.name, Category.color, Category.icon)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )

    return MonthlySummary(
        month=month,
        total_income=float(totals.get(TransactionType.income, 0.0)),
        total_expense=float(totals.get(TransactionType.expense, 0.0)),
        breakdown=[
            CategoryBreakdownItem(
                category_id=row.id,
                name=row.name,
                color=row.color,
                icon=row.icon,
                total=float(row.total),
            )
            for row in breakdown_rows
        ],
    )


@router.get("/trend", response_model=TrendSummary)
def trend_summary(
    months: int = Query(6, ge=1, le=24),
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    today = date.today()
    points: list[TrendPoint] = []
    for offset in range(-(months - 1), 1):
        year, month_num = _shift_month(today, offset)
        month_str = f"{year:04d}-{month_num:02d}"
        first, last = month_bounds(month_str)
        totals = dict(
            db.query(
                Transaction.type, func.coalesce(func.sum(Transaction.amount), 0.0)
            )
            .filter(
                Transaction.device_id == device_id,
                Transaction.date >= first,
                Transaction.date <= last,
            )
            .group_by(Transaction.type)
            .all()
        )
        points.append(
            TrendPoint(
                month=month_str,
                income=float(totals.get(TransactionType.income, 0.0)),
                expense=float(totals.get(TransactionType.expense, 0.0)),
            )
        )
    return TrendSummary(months=months, points=points)
