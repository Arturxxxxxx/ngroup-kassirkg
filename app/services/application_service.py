import uuid
from app.models.application import Application
from app.schemas.application import ApplicationDetail, ApplicationListItem
from sqlalchemy.orm import Session


def reject_list_applications(db: Session, uid_list: list[uuid.UUID]):
    apps = db.query(Application).filter(Application.id.in_(uid_list)).all()
    errors = []
    for app in apps:
        try:
            app.status = "REJECTED"
            app.reject_reason = "Отклонено админом"
            db.add(app)
        except Exception as e:
            errors.append((str(app.id), str(e)))
    db.commit()
    return errors


def accept_list_applications(db: Session, uid_list: list[uuid.UUID]):
    apps = db.query(Application).filter(Application.id.in_(uid_list)).all()
    errors = []
    for app in apps:
        try:
            app.status = "APPROVED"
            app.reject_reason = None
            db.add(app)
        except Exception as e:
            errors.append((str(app.id), str(e)))
    db.commit()
    return errors


def make_new_list_applications(db: Session, uid_list: list[uuid.UUID]):
    apps = db.query(Application).filter(Application.id.in_(uid_list)).all()
    errors = []
    for app in apps:
        try:
            app.status = "NEW"
            app.reject_reason = None
            db.add(app)
        except Exception as e:
            errors.append((str(app.id), str(e)))
    db.commit()
    return errors


def delete_list_applications(db: Session, uid_list: list[uuid.UUID]):
    apps = db.query(Application).filter(Application.id.in_(uid_list)).all()
    errors = []
    for app in apps:
        try:
            db.delete(app)
        except Exception as e:
            errors.append((str(app.id), str(e)))
    db.commit()
    return errors