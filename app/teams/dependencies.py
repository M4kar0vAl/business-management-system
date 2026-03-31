from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Path

from app.auth.dependencies import get_user_manager
from app.dependencies import UOWDep
from app.teams.services import TeamService

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
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
