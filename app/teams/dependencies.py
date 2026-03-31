from collections.abc import Callable
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Path

from app.auth.dependencies import get_user_manager
from app.auth.models import User
from app.dependencies import UOWDep
from app.teams.exceptions import UserDoesNotBelongToTeamError
from app.teams.models import Team
from app.teams.services import TeamService

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Awaitable
    from typing import Any

    from app.auth.user_manager import UserManager


async def get_team_service(
    uow: UOWDep, user_manager: Annotated[UserManager, Depends(get_user_manager)]
) -> AsyncGenerator[TeamService, Any]:
    yield TeamService(uow, user_manager)


TeamServiceDep = Annotated[TeamService, Depends(get_team_service)]


def current_team(full: bool = False):
    """
    Dependency factory to get task from `task_id` path parameter.

    :param full: boolean indicating whether to get task with all its relations
    :return: dependency for getting current task
    :raises TeamDoesNotExistError: if the task with the given id does not exist
    """

    async def _current_team(
        team_id: Annotated[int, Path()], team_service: TeamServiceDep
    ):
        return await team_service.get_team_by_id(team_id, full=full)

    return _current_team


def team_of_current_user(
    user_dep: Callable[..., User | Awaitable[User]], full: bool = False
):
    """
    Dependency factory to get team from `team_id` path parameter.

    Dependency will perform validation that user is a member of a team.

    :param user_dep: dependency for getting the user performing the action
    :param full: boolean indicating whether to get team with all its relations
    :return: dependency for getting the current team
    :raises TeamDoesNotExistError: if the task with the given id does not exist
    :raises UserDoesNotBelongToTeamError: if the user is not a member of a team
    """

    async def _team_of_current_user(
        team: Annotated[Team, Depends(current_team(full=full))],
        user: Annotated[User, Depends(user_dep)],
    ):
        if user.team_id != team.id:
            raise UserDoesNotBelongToTeamError(user, team.id)

        return team

    return _team_of_current_user
