import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DiscoveredQueryResponse(BaseModel):
    query_uuid: uuid.UUID = Field(validation_alias="uuid")
    query_text: str
    estimated_search_volume: int
    competitive_difficulty: int
    opportunity_score: float
    domain_visible: bool
    visibility_position: int | None
    discovered_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
