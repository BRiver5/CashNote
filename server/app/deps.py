import uuid

from fastapi import Header, HTTPException


def get_device_id(x_device_id: str = Header(..., alias="X-Device-Id")) -> str:
    try:
        uuid.UUID(x_device_id)
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid X-Device-Id header")
    return x_device_id
