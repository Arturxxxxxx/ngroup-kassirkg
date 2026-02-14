from sqlalchemy.orm import Session
from app.models import File


def create_file(db: Session, f: File) -> File:
    db.add(f)
    db.flush()
    return f


def get_file(db: Session, file_id):
    return db.query(File).filter(File.id == file_id).first()
