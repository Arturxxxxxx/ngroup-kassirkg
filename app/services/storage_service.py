import os
from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings
from app.core.exceptions import bad_request
from app.models import File

ALLOWED_MIME = {"application/pdf", "image/jpeg", "image/png"}


def ensure_dirs():
    root = Path(settings.STORAGE_ROOT)
    (root / settings.BIRTH_CERTS_DIR).mkdir(parents=True, exist_ok=True)


def validate_upload(file: UploadFile):
    if file.content_type not in ALLOWED_MIME:
        raise bad_request("Unsupported file type. Allowed: pdf, jpg, png")


def save_upload_to_disk(file_id, upload: UploadFile) -> tuple[str, int]:
    ensure_dirs()

    ext = ""
    if upload.filename and "." in upload.filename:
        ext = "." + upload.filename.rsplit(".", 1)[-1].lower()

    rel = f"{settings.BIRTH_CERTS_DIR}/{file_id}{ext}"
    abs_path = Path(settings.STORAGE_ROOT) / rel
    tmp_path = str(abs_path) + ".tmp"

    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    written = 0

    with open(tmp_path, "wb") as out:
        while True:
            chunk = upload.file.read(1024 * 1024)
            if not chunk:
                break
            written += len(chunk)
            if written > max_bytes:
                out.close()
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
                raise bad_request(f"File too large. Max {settings.MAX_UPLOAD_MB}MB")
            out.write(chunk)

    os.replace(tmp_path, abs_path)
    return rel, written


def file_entity(file_id, rel_path: str, upload: UploadFile, size: int) -> File:
    return File(
        id=file_id,
        storage_path=rel_path,
        original_name=upload.filename or "file",
        mime=upload.content_type or "application/octet-stream",
        size=size,
    )
