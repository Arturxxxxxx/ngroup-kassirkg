from pydantic import BaseModel, Field

class RejectApplicationRequest(BaseModel):
    reason: str = Field(min_length=2, max_length=500)