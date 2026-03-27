from pydantic import BaseModel


class BaseResponse(BaseModel):
    detail: str


class ErrorResponse(BaseResponse):
    pass


class SuccessResponse(BaseResponse):
    pass
