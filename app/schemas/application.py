from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class ChildCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    age: int = Field(ge=0, le=18)


class ApplicationCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    whatsapp_phone: str = Field(min_length=5, max_length=64)
    email: str = Field(min_length=5, max_length=64)

    is_investor: bool
    objects: List[str] = Field(default_factory=list)
    contract_number: Optional[str] = Field(default=None, max_length=128)

    children_total: int = Field(ge=0, le=20)
    children_coming: int = Field(ge=0, le=20)

    consent: bool
    children: List[ChildCreate] = Field(default_factory=list)


class ApplicationCreateResponse(BaseModel):
    application_id: UUID
    status: str


class ApplicationListItem(BaseModel):
    id: UUID
    base_id: int
    full_name: str
    whatsapp_phone: str
    is_investor: bool
    objects: List[str]
    contract_number: Optional[str]
    children_total: int
    children_coming: int
    email: Optional[str] = None
    status: str
    created_at: datetime


class ApplicationListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[ApplicationListItem]


class ChildView(BaseModel):
    id: UUID
    full_name: str
    age: int
    path_image: str


class ApplicationDetail(BaseModel):
    id: UUID
    full_name: str
    whatsapp_phone: str
    email: Optional[str] = None
    is_investor: bool
    objects: List[str]
    contract_number: Optional[str]
    children_total: int
    children_coming: int
    consent: bool
    status: str
    reject_reason: Optional[str]
    created_at: datetime
    children: List[ChildView]
