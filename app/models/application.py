import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base


class ApplicationStatus(str, enum.Enum):
    NEW = "NEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    whatsapp_phone: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str] = mapped_column(String(225), nullable=False, index=True)

    is_investor: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    objects: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    contract_number: Mapped[str | None] = mapped_column(String(128), nullable=True)

    children_total: Mapped[int] = mapped_column(Integer, nullable=False)
    children_coming: Mapped[int] = mapped_column(Integer, nullable=False)

    consent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.NEW)
    reject_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    children = relationship("Child", back_populates="application", cascade="all, delete-orphan")
