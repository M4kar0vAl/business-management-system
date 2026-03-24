from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


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
