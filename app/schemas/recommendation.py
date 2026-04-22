from pydantic import BaseModel, ConfigDict, Field
import uuid

class ContentRecommendationResponse(BaseModel):
    recommendation_uuid: uuid.UUID = Field(validation_alias="uuid")
    target_query_uuid: uuid.UUID = Field(validation_alias="query_uuid")
    content_type: str
    title: str
    rationale: str
    target_keywords: list[str]
    priority: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)