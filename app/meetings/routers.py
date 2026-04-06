from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query, status
from pydantic import EmailStr

from app import responses
from app.auth.fastapi_users_instance import current_active_user, get_current_manager
from app.auth.models import User
from app.meetings.dependencies import MeetingServiceDep, current_meeting
from app.meetings.models import Meeting
from app.meetings.schemas import (
    MeetingCreate,
    MeetingFilters,
    MeetingRead,
    MeetingReadFull,
)

router = APIRouter(
    prefix="/meetings",
    tags=["Meetings"],
    dependencies=[Depends(current_active_user)],
    responses={**responses.UNAUTHORIZED_RESPONSE},
)
meeting_detail_router = APIRouter(
    prefix="/{meeting_id}", responses={**responses.NOT_FOUND_RESPONSE}
)


ROUTE_NAME_PREFIX = "meetings"
GET_MEETINGS_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:list"
GET_USER_MEETINGS_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:get_of_user"
GET_MEETING_BY_ID_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:retrieve"
CREATE_MEETING_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:create"
DELETE_MEETING_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:delete"
ADD_MEETING_PARTICIPANT_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:add_participant"
REMOVE_MEETING_PARTICIPANT_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:remove_participant"


@router.get("/", response_model=list[MeetingRead], name=GET_MEETINGS_ROUTE_NAME)
async def get_meetings(
    filters: Annotated[MeetingFilters, Query()], meetings_service: MeetingServiceDep
):
    """
    Get all meetings. Supports filtering.

    Active users only.
    """
    return await meetings_service.get_meetings_list(filters)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=MeetingRead,
    dependencies=[Depends(get_current_manager)],
    responses={**responses.BAD_REQUEST_RESPONSE},
    name=CREATE_MEETING_ROUTE_NAME,
)
async def create_meeting(meeting: MeetingCreate, meetings_service: MeetingServiceDep):
    """
    Create a new meeting.

    In order to create a meeting:
    - its time interval should not overlap with other meetings.

    Active manager or admin only.
    """
    created_meeting = await meetings_service.create_meeting(meeting)
    await meetings_service.uow.flush()
    return created_meeting


@router.get("/my", response_model=list[MeetingRead], name=GET_USER_MEETINGS_ROUTE_NAME)
async def get_user_meetings(
    filters: Annotated[MeetingFilters, Query()],
    user: Annotated[User, Depends(current_active_user)],
    meetings_service: MeetingServiceDep,
):
    """
    Get all meetings where the current user is participant.

    Active users only.
    """
    return await meetings_service.get_user_meetings(user, filters)


@meeting_detail_router.get(
    "/", response_model=MeetingReadFull, name=GET_MEETING_BY_ID_ROUTE_NAME
)
async def get_meeting_by_id(
    meeting: Annotated[
        Meeting, Depends(current_meeting(current_active_user, full=True))
    ],
):
    """
    Get a meeting by ID.

    Active users only.
    """
    return meeting


@meeting_detail_router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**responses.FORBIDDEN_RESPONSE},
    name=DELETE_MEETING_ROUTE_NAME,
)
async def delete_meeting(
    meeting: Annotated[
        Meeting, Depends(current_meeting(current_active_user, author=True))
    ],
    meetings_service: MeetingServiceDep,
):
    """
    Delete a meeting.

    In order to delete a meeting:
    - meeting with id `meeting_id` must exist
    - current user must be the one who created the meeting

    Active users only.
    """
    await meetings_service.delete_meeting(meeting)


@meeting_detail_router.post(
    "/participants",
    responses={**responses.SUCCESS_RESPONSE, **responses.BAD_REQUEST_RESPONSE},
    name=ADD_MEETING_PARTICIPANT_ROUTE_NAME,
)
async def add_participant(
    user_email: Annotated[EmailStr, Body(embed=True)],
    meeting: Annotated[Meeting, Depends(current_meeting(get_current_manager))],
    meetings_service: MeetingServiceDep,
):
    """
    Add a participant to a meeting.

    In order to add a participant:
    - meeting with id `meeting_id` must exist
    - user with email `user_email` must exist
    - user with email `user_email` should not be the participant of the meeting

    Active manager or admin only.
    """
    await meetings_service.add_participant(meeting, user_email)
    return {"detail": "Added participant successfully"}


@meeting_detail_router.delete(
    "/participants/{participant_id}",
    responses={**responses.SUCCESS_RESPONSE},
    name=REMOVE_MEETING_PARTICIPANT_ROUTE_NAME,
)
async def remove_participant(
    participant_id: int,
    meeting: Annotated[Meeting, Depends(current_meeting(get_current_manager))],
    meetings_service: MeetingServiceDep,
):
    """
    Remove a participant from the meeting.

    In order to remove a participant:
    - meeting with id `meeting_id` must exist
    - user with id `participant_id` must exist

    Active manager or admin only.
    """
    await meetings_service.remove_participant(meeting, participant_id)
    return {"detail": "Removed participant successfully"}


router.include_router(meeting_detail_router)
