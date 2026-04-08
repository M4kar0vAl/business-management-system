from typing import Any

from fastapi import HTTPException, status
from starlette.datastructures import URL


class ForbiddenError(HTTPException):
    def __init__(
        self,
        detail: Any = "You do not have permission to perform this action",
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail=detail, headers=headers
        )


class RedirectException(HTTPException):
    def __init__(
        self,
        url: str | URL,
        status_code: int = status.HTTP_303_SEE_OTHER,
        headers: dict[str, str] | None = None,
    ):
        self.url = url
        super().__init__(status_code=status_code, detail="Redirect", headers=headers)
