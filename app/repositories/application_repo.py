from sqlalchemy.orm import Session, joinedload
from sqlalchemy import exists, func, case, desc
from app.models import Application, ApplicationStatus
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
    email: Optional[str],
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

    priority = case(
        (Application.status == ApplicationStatus.APPROVED, 1),
        (Application.status == ApplicationStatus.NEW, 2),
        (Application.status == ApplicationStatus.REJECTED, 3),
        else_=4,
    )

    total = q.count()
    items = (
        q.order_by(
            priority.asc(),
    desc(Application.updated_at).nullslast(),
            desc(Application.created_at).nullslast(),
        )
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return total, items


def get_registration_status_by_email(db: Session, email: str):
    # приоритет статусов
    priority = case(
        (Application.status == ApplicationStatus.APPROVED, 1),
        (Application.status == ApplicationStatus.NEW, 2),
        (Application.status == ApplicationStatus.REJECTED, 3),
        else_=4,
    )

    row = (
        db.query(Application.status)
        .filter(Application.email == email)
        .order_by(priority)
        .first()
    )

    if not row:
        return None

    return row.status.value

