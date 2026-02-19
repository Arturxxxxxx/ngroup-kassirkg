import json
import uuid
from fastapi import APIRouter, Depends, UploadFile, File as UploadFileParam, Form
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.exceptions import bad_request
from app.models import Application, Child
from app.schemas.application import ApplicationCreate, ApplicationCreateResponse
from app.repositories.application_repo import create_application
from app.repositories.file_repo import create_file
from app.services.storage_service import validate_upload, save_upload_to_disk, file_entity

router = APIRouter(prefix="/public", tags=["public"])


@router.post("/applications", response_model=ApplicationCreateResponse)
def create_application_public(
    payload: str = Form(...),                        # JSON string
    files: list[UploadFile] = UploadFileParam(...),  # files[] count == children count
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
    if len(files) != len(dto.children):
        raise bad_request("files count must match children count")

    for f in files:
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
    db.flush()  # children ids available

    for idx, child in enumerate(app.children):
        upload = files[idx]
        file_id = uuid.uuid4()
        rel_path, size = save_upload_to_disk(file_id, upload)
        f_entity = file_entity(file_id, rel_path, upload, size)
        create_file(db, f_entity)
        child.birth_cert_file_id = f_entity.id

    db.commit()
    return ApplicationCreateResponse(application_id=app.id, status=app.status.value)
