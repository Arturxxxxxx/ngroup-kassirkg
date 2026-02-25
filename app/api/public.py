import json
import uuid
from fastapi import APIRouter, Depends, UploadFile, File as UploadFileParam, Form, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.exceptions import bad_request
from app.models import Application, Child
from app.schemas.application import ApplicationCreate, ApplicationCreateResponse
from app.repositories.application_repo import create_application, get_registration_status_by_email
from app.repositories.file_repo import create_file
from app.services.storage_service import validate_upload, save_upload_to_disk, file_entity


router = APIRouter(prefix="/public", tags=["public"])


@router.post("/applications", response_model=ApplicationCreateResponse)
def create_application_public(
    payload: str = Form(...),

    # старый формат
    files: list[UploadFile] | None = UploadFileParam(default=None),

    # новый формат
    files1: list[UploadFile] | None = UploadFileParam(default=None),
    files2: list[UploadFile] | None = UploadFileParam(default=None),

    db: Session = Depends(get_db),
):
    try:
        dto = ApplicationCreate.model_validate(json.loads(payload))
    except Exception:
        raise bad_request("Invalid payload JSON")

    if dto.children_coming > dto.children_total:
        raise bad_request("children_coming must be <= children_total")
    if not dto.consent:
        raise bad_request("consent must be true")
    if dto.is_investor and len(dto.objects) == 0:
        raise bad_request("objects must be non-empty for investor")

    # нормализуем вход к двум массивам
    if files1 is None and files2 is None:
        # старый формат обязателен: files
        if not files:
            raise bad_request("files (old) or files1/files2 (new) are required")
        if len(files) != len(dto.children):
            raise bad_request("files count must match children count")
        f1_list = files
        f2_list = [None] * len(files)
    else:
        # новый формат: files1 обязателен, files2 можно сделать опциональным
        if not files1:
            raise bad_request("files1 is required")
        if len(files1) != len(dto.children):
            raise bad_request("files1 count must match children count")

        if files2 is None:
            files2 = [None] * len(files1)
        elif len(files2) != len(dto.children):
            raise bad_request("files2 count must match children count")

        f1_list = files1
        f2_list = files2

    # валидация
    for f in f1_list:
        validate_upload(f)
    for f in f2_list:
        if f is not None:
            validate_upload(f)

    app = Application(
        email=dto.email,
        full_name=dto.full_name,
        whatsapp_phone=dto.whatsapp_phone,
        is_investor=dto.is_investor,
        objects=dto.objects,
        contract_number=dto.contract_number,
        children_total=dto.children_total,
        children_coming=dto.children_coming,
        consent=dto.consent,
    )

    for c in dto.children:
        app.children.append(Child(full_name=c.full_name, age=c.age))

    create_application(db, app)
    db.flush()

    for idx, child in enumerate(app.children):
        # файл 1 (всегда)
        upload1 = f1_list[idx]
        file_id1 = uuid.uuid4()
        rel1, size1 = save_upload_to_disk(file_id1, upload1)
        fe1 = file_entity(file_id1, rel1, upload1, size1)
        create_file(db, fe1)
        child.birth_cert_file_id = fe1.id

        # файл 2 (опционально)
        upload2 = f2_list[idx]
        if upload2 is not None:
            file_id2 = uuid.uuid4()
            rel2, size2 = save_upload_to_disk(file_id2, upload2)
            fe2 = file_entity(file_id2, rel2, upload2, size2)
            create_file(db, fe2)
            child.birth_cert_file2_id = fe2.id

    db.commit()
    return ApplicationCreateResponse(application_id=app.id, status=app.status.value)


@router.get("/registrations/check")
def check_registration(
    email: str = Query(..., min_length=3),
    db: Session = Depends(get_db),
):
    if not email:
        raise bad_request("email required")

    status = get_registration_status_by_email(db, email)

    if not status:
        return {"registered": False}

    return {
        "registered": True,
        "status": status  # APPROVED / NEW / REJECTED
    }