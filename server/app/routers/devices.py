from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_device_id
from ..models import Category, Device, SavingGoal, Transaction
from ..schemas.device import DeviceRegisterResponse, DeviceResetResponse
from ..seed import seed_default_categories

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/register", response_model=DeviceRegisterResponse)
def register_device(
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    device = db.get(Device, device_id)
    created = False
    if device is None:
        device = Device(id=device_id)
        db.add(device)
        db.commit()
        db.refresh(device)
        created = True
    seeded = seed_default_categories(db, device_id)
    return DeviceRegisterResponse(device=device, created=created, categories_seeded=seeded)


@router.post("/reset", response_model=DeviceResetResponse)
def reset_device(
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    tx_deleted = (
        db.query(Transaction).filter(Transaction.device_id == device_id).delete()
    )
    goals_deleted = (
        db.query(SavingGoal).filter(SavingGoal.device_id == device_id).delete()
    )
    cats_deleted = (
        db.query(Category).filter(Category.device_id == device_id).delete()
    )
    db.commit()

    device = db.get(Device, device_id)
    if device is None:
        db.add(Device(id=device_id))
        db.commit()
    seeded = seed_default_categories(db, device_id)
    return DeviceResetResponse(
        transactions_deleted=tx_deleted,
        categories_deleted=cats_deleted,
        goals_deleted=goals_deleted,
        categories_seeded=seeded,
    )
