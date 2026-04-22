from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
import uuid


class ProfileCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    domain: str = Field(..., min_length=3, max_length=255)
    industry: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    competitors: list[str] = Field(default_factory=list, max_length=10)


class ProfileResponse(BaseModel):
    profile_uuid: uuid.UUID = Field(validation_alias="uuid")
    name: str
    domain: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ProfileDetailResponse(ProfileResponse):
    total_queries_discovered: int = 0
    avg_opportunity_score: float = 0.0