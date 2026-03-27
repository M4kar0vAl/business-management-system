from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.auth.exception_handlers import (
    exception_status_mapping as auth_exception_status_mapping,
)
from app.teams.exception_handlers import (
    exception_status_mapping as teams_exception_status_mapping,
)


def exception_handler_factory(
    app: FastAPI, exc_type: type[Exception], status_code: int
):
    """
    Exception handler factory.

    :param app: fastapi app to register exception handlers for
    :param exc_type: exception class to register handler for
    :param status_code: http status code to return in response
    :return: exception handler
    """

    @app.exception_handler(exc_type)
    async def handler(_: Request, exc: Exception):
        message = getattr(exc, "message", str(exc))

        return JSONResponse(status_code=status_code, content={"detail": message})

    return handler


def register_exception_handlers_from_mapping(
    app: FastAPI, exception_status_mapping: dict[type[Exception], int]
) -> None:
    """
    Register exception handlers from {exception: status code} mapping.

    :param app: fastapi app to register exception handlers for
    :param exception_status_mapping: a dictionary mapping exception class to http status code
    :return: None
    """
    for exc_type, status_code in exception_status_mapping.items():
        exception_handler_factory(app, exc_type, status_code)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register exception handlers for fastapi app.

    :param app: fastapi app to register exception handlers for
    :return: None
    """
    register_exception_handlers_from_mapping(app, auth_exception_status_mapping)
    register_exception_handlers_from_mapping(app, teams_exception_status_mapping)
