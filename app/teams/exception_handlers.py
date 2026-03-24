from fastapi import FastAPI, status

from app.exception_handlers import exception_handler_factory
from app.teams.exceptions import (
    TeamAlreadyExistsError,
    TeamDoesNotExistError,
    UserAlreadyInTeamError,
    UserNotInTeamError,
)

exception_status_mapping = {
    TeamDoesNotExistError: status.HTTP_404_NOT_FOUND,
    TeamAlreadyExistsError: status.HTTP_400_BAD_REQUEST,
    UserAlreadyInTeamError: status.HTTP_400_BAD_REQUEST,
    UserNotInTeamError: status.HTTP_400_BAD_REQUEST,
}


def register_exception_handlers(app: FastAPI):
    for exc_type, status_code in exception_status_mapping.items():
        exception_handler_factory(app, exc_type, status_code)
