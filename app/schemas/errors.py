from pydantic import BaseModel

class ErrorDetail(BaseModel):
    loc: list[str] | None = None
    msg: str
    type: str

class ErrorResponse(BaseModel):
    error: str
    details: list[ErrorDetail] | None = None