from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

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
