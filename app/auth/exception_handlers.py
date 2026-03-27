from fastapi import FastAPI, status
from fastapi_users.exceptions import UserNotExists

from app.exception_handlers import exception_handler_factory

exception_status_mapping = {
    UserNotExists: status.HTTP_404_NOT_FOUND,
}


def register_exception_handlers(app: FastAPI):
    for exc_type, status_code in exception_status_mapping.items():
        exception_handler_factory(app, exc_type, status_code)
