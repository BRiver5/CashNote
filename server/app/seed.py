from sqlalchemy.orm import Session

from .models import Category

DEFAULT_CATEGORIES = [
    {"name": "Food", "color": "#E8790C", "icon": "🍔"},
    {"name": "Transport", "color": "#2FA98C", "icon": "🚗"},
    {"name": "Entertainment", "color": "#3D7DD1", "icon": "🎬"},
    {"name": "Shopping", "color": "#F4B740", "icon": "🛍️"},
    {"name": "Health", "color": "#E8790C", "icon": "💊"},
    {"name": "Bills", "color": "#2FA98C", "icon": "🧾"},
    {"name": "Groceries", "color": "#3D7DD1", "icon": "🛒"},
    {"name": "Other", "color": "#F4B740", "icon": "🗂️"},
]


def seed_default_categories(db: Session, device_id: str) -> int:
    existing = (
        db.query(Category).filter(Category.device_id == device_id).count()
    )
    if existing > 0:
        return 0
    for spec in DEFAULT_CATEGORIES:
        db.add(
            Category(
                device_id=device_id,
                name=spec["name"],
                color=spec["color"],
                icon=spec["icon"],
                monthly_budget=None,
                is_default=True,
            )
        )
    db.commit()
    return len(DEFAULT_CATEGORIES)
