from typing import Any

from fastapi import HTTPException, status


class ForbiddenError(HTTPException):
    def __init__(
        self,
        detail: Any = "You do not have permission to perform this action",
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail=detail, headers=headers
        )
