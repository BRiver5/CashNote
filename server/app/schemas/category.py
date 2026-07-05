from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=60)
    color: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: str = Field(..., min_length=1, max_length=16)
    monthly_budget: float | None = Field(None, ge=0)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=60)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: str | None = Field(None, min_length=1, max_length=16)
    monthly_budget: float | None = Field(None, ge=0)
    clear_budget: bool = False


class CategoryOut(CategoryBase):
    model_config = {"from_attributes": True}

    id: int
    is_default: bool
