from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_device_id
from ..models import Category, Transaction
from ..schemas.category import CategoryCreate, CategoryOut, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


def _get_owned_category(db: Session, device_id: str, category_id: int) -> Category:
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.device_id == device_id)
        .first()
    )
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("", response_model=list[CategoryOut])
def list_categories(
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    return (
        db.query(Category)
        .filter(Category.device_id == device_id)
        .order_by(Category.is_default.desc(), Category.id.asc())
        .all()
    )


@router.post("", response_model=CategoryOut, status_code=201)
def create_category(
    payload: CategoryCreate,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    duplicate = (
        db.query(Category)
        .filter(Category.device_id == device_id, Category.name == payload.name)
        .first()
    )
    if duplicate is not None:
        raise HTTPException(status_code=409, detail="Category with this name already exists")
    category = Category(
        device_id=device_id,
        name=payload.name,
        color=payload.color,
        icon=payload.icon,
        monthly_budget=payload.monthly_budget,
        is_default=False,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    category = _get_owned_category(db, device_id, category_id)
    if payload.name is not None:
        duplicate = (
            db.query(Category)
            .filter(
                Category.device_id == device_id,
                Category.name == payload.name,
                Category.id != category_id,
            )
            .first()
        )
        if duplicate is not None:
            raise HTTPException(status_code=409, detail="Category with this name already exists")
        category.name = payload.name
    if payload.color is not None:
        category.color = payload.color
    if payload.icon is not None:
        category.icon = payload.icon
    if payload.clear_budget:
        category.monthly_budget = None
    elif payload.monthly_budget is not None:
        category.monthly_budget = payload.monthly_budget
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    category = _get_owned_category(db, device_id, category_id)
    if category.is_default:
        raise HTTPException(status_code=409, detail="Default categories can't be deleted")

    fallback = (
        db.query(Category)
        .filter(
            Category.device_id == device_id,
            Category.name == "Other",
            Category.id != category_id,
        )
        .first()
    )
    if fallback is None:
        fallback = (
            db.query(Category)
            .filter(
                Category.device_id == device_id,
                Category.is_default.is_(True),
                Category.id != category_id,
            )
            .order_by(Category.id.asc())
            .first()
        )
    if fallback is None:
        raise HTTPException(
            status_code=409,
            detail="Can't delete the only remaining category",
        )

    db.query(Transaction).filter(
        Transaction.device_id == device_id,
        Transaction.category_id == category_id,
    ).update({Transaction.category_id: fallback.id})

    db.delete(category)
    db.commit()
