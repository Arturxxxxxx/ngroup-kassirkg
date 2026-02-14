from sqlalchemy.orm import Session, joinedload
from app.models import Application
from datetime import datetime
from typing import Optional


def create_application(db: Session, app: Application) -> Application:
    db.add(app)
    db.flush()
    return app


def get_application_detail(db: Session, app_id):
    return (
        db.query(Application)
        .options(joinedload(Application.children))
        .filter(Application.id == app_id)
        .first()
    )


def list_applications(
    db: Session,
    page: int,
    per_page: int,
    status: Optional[str],
    is_investor: Optional[bool],
    object_value: Optional[str],
    phone_search: Optional[str],
    created_from: Optional[datetime],
    created_to: Optional[datetime],
):
    q = db.query(Application)

    if status:
        q = q.filter(Application.status == status)

    if is_investor is not None:
        q = q.filter(Application.is_investor == is_investor)

    if object_value:
        q = q.filter(Application.objects.contains([object_value]))

    if phone_search:
        q = q.filter(Application.whatsapp_phone.ilike(f"%{phone_search}%"))

    if created_from:
        q = q.filter(Application.created_at >= created_from)
    if created_to:
        q = q.filter(Application.created_at <= created_to)

    total = q.count()
    items = (
        q.order_by(Application.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return total, items
