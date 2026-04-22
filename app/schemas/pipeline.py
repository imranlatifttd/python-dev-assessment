from pydantic import BaseModel, ConfigDict, Field
import uuid


class PipelineRunResponse(BaseModel):
    run_uuid: uuid.UUID = Field(validation_alias="uuid")
    status: str
    queries_discovered: int
    queries_scored: int
    tokens_used: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)