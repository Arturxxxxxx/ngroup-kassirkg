from sqlalchemy.orm import Session
from app.models import Child


def get_child(db: Session, child_id):
    return db.query(Child).filter(Child.id == child_id).first()
