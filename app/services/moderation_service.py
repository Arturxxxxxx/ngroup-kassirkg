from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Child, Application, ChildStatus, ApplicationStatus, AuditLog


def recompute_application_status(db: Session, application_id):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        return

    statuses = [c.status for c in app.children]

    if not statuses:
        app.status = ApplicationStatus.NEW
        return

    if all(s == ChildStatus.APPROVED for s in statuses):
        app.status = ApplicationStatus.APPROVED
    elif all(s == ChildStatus.REJECTED for s in statuses):
        app.status = ApplicationStatus.REJECTED
    elif any(s == ChildStatus.PENDING for s in statuses):
        # есть еще непроверенные и уже есть решения -> все равно PARTIAL,
        # иначе NEW. Упростим: если есть хотя бы одно решение -> PARTIAL.
        has_decision = any(s in (ChildStatus.APPROVED, ChildStatus.REJECTED) for s in statuses)
        app.status = ApplicationStatus.PARTIAL if has_decision else ApplicationStatus.NEW
    else:
        app.status = ApplicationStatus.PARTIAL


def approve_child(db: Session, child: Child, actor: str):
    child.status = ChildStatus.APPROVED
    child.reject_reason = None
    child.checked_by = actor
    child.checked_at = datetime.utcnow()

    db.add(AuditLog(
        actor=actor,
        entity_type="child",
        entity_id=str(child.id),
        action="approve",
        payload={"application_id": str(child.application_id)},
    ))

    recompute_application_status(db, child.application_id)


def reject_child(db: Session, child: Child, actor: str, reason: str):
    child.status = ChildStatus.REJECTED
    child.reject_reason = reason
    child.checked_by = actor
    child.checked_at = datetime.utcnow()

    db.add(AuditLog(
        actor=actor,
        entity_type="child",
        entity_id=str(child.id),
        action="reject",
        payload={"application_id": str(child.application_id), "reason": reason},
    ))

    recompute_application_status(db, child.application_id)
