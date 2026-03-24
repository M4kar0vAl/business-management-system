from fastapi import FastAPI, Request, status
from starlette.responses import JSONResponse

from app.teams.exceptions import (
    TeamAlreadyExistsError,
    TeamDoesNotExistError,
    UserAlreadyInTeamError,
    UserNotInTeamError,
)


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(TeamDoesNotExistError)
    async def team_does_not_exist_exception_handler(
        _: Request, exc: TeamDoesNotExistError
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.message}
        )

    @app.exception_handler(TeamAlreadyExistsError)
    async def team_already_exists_exception_handler(
        _: Request, exc: TeamAlreadyExistsError
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.message}
        )

    @app.exception_handler(UserAlreadyInTeamError)
    async def user_already_in_team_exception_handler(
        _: Request, exc: UserAlreadyInTeamError
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.message}
        )

    @app.exception_handler(UserNotInTeamError)
    async def user_not_in_team_exception_handler(_: Request, exc: UserNotInTeamError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.message}
        )
