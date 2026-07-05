from datetime import datetime

from pydantic import BaseModel


class DeviceOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    created_at: datetime


class DeviceRegisterResponse(BaseModel):
    device: DeviceOut
    created: bool
    categories_seeded: int


class DeviceResetResponse(BaseModel):
    transactions_deleted: int
    categories_deleted: int
    goals_deleted: int
    categories_seeded: int
