from fastapi import status

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
