from pydantic import BaseModel
from typing import Optional


class AdminApplicationFilters(BaseModel):
    status: Optional[str] = None
    is_investor: Optional[bool] = None
    object: Optional[str] = None
    phone_search: Optional[str] = None
    has_pending_children: Optional[bool] = None
    created_from: Optional[str] = None  # ISO date string "2026-02-01"
    created_to: Optional[str] = None
