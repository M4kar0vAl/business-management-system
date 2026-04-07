from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Path

from app.auth.dependencies import get_user_manager
from app.auth.user_manager import UserManager
from app.dependencies import UOWDep
from app.http_exceptions import ForbiddenError
from app.meetings.services import MeetingService

if TYPE_CHECKING:
    from app.auth.models import User


async def get_meeting_service(
    uow: UOWDep, user_manager: Annotated[UserManager, Depends(get_user_manager)]
):
    yield MeetingService(uow, user_manager)


MeetingServiceDep = Annotated[MeetingService, Depends(get_meeting_service)]


def current_meeting(
    user_dep: Callable[..., User | Awaitable[User]],
    full: bool = False,
    author: bool = False,
):
    """
    Dependency factory to get meeting from `meeting_id` path parameter.

    :param user_dep: dependency for getting the user performing the action
    :param full: boolean indicating whether to get meeting with all its relations
    :param author: boolean indicating whether to check that user is the one who created the meeting
    :return: dependency for getting the current meeting
    :raises MeetingDoesNotExistError: if the meeting with the given id does not exist
    :raises ForbiddenError: if author is True and the user is not an author of the task
    """

    async def _current_meeting(
        meeting_id: Annotated[int, Path()],
        user: Annotated[User, Depends(user_dep)],
        meeting_service: MeetingServiceDep,
    ):
        meeting = await meeting_service.get_meeting_by_id(meeting_id, full=full)

        if author and meeting.created_by_id != user.id:
            raise ForbiddenError()

        return meeting

    return _current_meeting
