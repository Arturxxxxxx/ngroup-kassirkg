import uuid
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path

from app.core.db import get_db
from app.core.security import require_admin, create_access_token
from app.core.config import settings
from app.core.exceptions import bad_request, not_found

from app.models import ApplicationStatus, AuditLog

from app.schemas.application import ApplicationListResponse, ApplicationListItem, ApplicationDetail, ChildView
from app.schemas.admin import RejectApplicationRequest
from app.repositories.application_repo import list_applications, get_application_detail
from app.repositories.file_repo import get_file

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/auth/login")
def admin_login(body: dict):
    username = body.get("username")
    password = body.get("password")

    if username != settings.ADMIN_USERNAME or password != settings.ADMIN_PASSWORD:
        raise bad_request("Invalid credentials")

    return {"access_token": create_access_token(subject=username), "token_type": "bearer"}


@router.get("/applications", response_model=ApplicationListResponse)
def admin_list_applications(
    page: int = 1,
    per_page: int = 1000,
    status: str | None = None,
    is_investor: bool | None = None,
    object: str | None = None,
    phone_search: str | None = None,
    created_from: str | None = None,
    created_to: str | None = None,
    email: str | None = None,
    db: Session = Depends(get_db),
    actor: str = Depends(require_admin),
):
    if page < 1 or per_page < 1 or per_page > 1001:
        raise bad_request("Invalid pagination")

    dt_from = datetime.fromisoformat(created_from) if created_from else None
    dt_to = datetime.fromisoformat(created_to) if created_to else None

    total, rows = list_applications(
        db=db,
        page=page,
        per_page=per_page,
        status=status,
        is_investor=is_investor,
        object_value=object,
        email=email,
        phone_search=phone_search,
        created_from=dt_from,
        created_to=dt_to,
    )

    items = [
        ApplicationListItem(
            id=r.id,
            full_name=r.full_name,
            whatsapp_phone=r.whatsapp_phone,
            is_investor=r.is_investor,
            objects=r.objects,
            email=r.email,
            contract_number=r.contract_number,
            children_total=r.children_total,
            children_coming=r.children_coming,
            status=r.status.value,
            created_at=r.created_at,
        )
        for r in rows
    ]
    return ApplicationListResponse(total=total, page=page, per_page=per_page, items=items)


@router.get("/applications/{app_id}", response_model=ApplicationDetail)
def admin_get_application(app_id: uuid.UUID, db: Session = Depends(get_db), actor: str = Depends(require_admin)):
    app = get_application_detail(db, app_id)
    if not app:
        raise not_found("Application not found")

    return ApplicationDetail(
        id=app.id,
        full_name=app.full_name,
        whatsapp_phone=app.whatsapp_phone,
        is_investor=app.is_investor,
        objects=app.objects,
        contract_number=app.contract_number,
        children_total=app.children_total,
        email=app.email,
        children_coming=app.children_coming,
        consent=app.consent,
        status=app.status.value,
        reject_reason=app.reject_reason,
        created_at=app.created_at,
        children=[
            ChildView(
                id=c.id,
                full_name=c.full_name,
                age=c.age,
                path_image=(f"/admin/files/{c.birth_cert_file_id}")
            )
            for c in app.children
        ],
    )


@router.post("/applications/{app_id}/approve")
def admin_approve_application(app_id: uuid.UUID, db: Session = Depends(get_db), actor: str = Depends(require_admin)):
    app = get_application_detail(db, app_id)
    if not app:
        raise not_found("Application not found")

    app.status = ApplicationStatus.APPROVED
    app.reject_reason = None

    db.add(AuditLog(
        actor=actor,
        entity_type="application",
        entity_id=str(app.id),
        action="approve",
        payload={},
    ))

    db.commit()
    return {"ok": True}


@router.post("/applications/{app_id}/reject")
def admin_reject_application(
    app_id: uuid.UUID,
    payload: RejectApplicationRequest,
    db: Session = Depends(get_db),
    actor: str = Depends(require_admin),
):
    app = get_application_detail(db, app_id)
    if not app:
        raise not_found("Application not found")

    app.status = ApplicationStatus.REJECTED
    app.reject_reason = payload.reason

    db.add(AuditLog(
        actor=actor,
        entity_type="application",
        entity_id=str(app.id),
        action="reject",
        payload={"reason": payload.reason},
    ))

    db.commit()
    return {"ok": True}


@router.get("/files/{file_id}")
def admin_get_file(file_id: uuid.UUID, db: Session = Depends(get_db), actor: str = Depends(require_admin)):
    f = get_file(db, file_id)
    if not f:
        raise not_found("File not found")

    abs_path = Path(settings.STORAGE_ROOT) / f.storage_path
    if not abs_path.exists():
        raise not_found("File missing on disk")

    return FileResponse(path=str(abs_path), media_type=f.mime, filename=f.original_name)

