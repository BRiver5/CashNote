from pydantic import BaseModel


class CategoryBreakdownItem(BaseModel):
    category_id: int
    name: str
    color: str
    icon: str
    total: float


class MonthlySummary(BaseModel):
    month: str
    total_income: float
    total_expense: float
    breakdown: list[CategoryBreakdownItem]


class TrendPoint(BaseModel):
    month: str
    income: float
    expense: float


class TrendSummary(BaseModel):
    months: int
    points: list[TrendPoint]
