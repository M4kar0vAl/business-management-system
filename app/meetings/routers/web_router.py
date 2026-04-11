from contextlib import suppress
from datetime import UTC, datetime
from typing import Annotated

import pytz
from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi_users.exceptions import UserNotExists
from pydantic import EmailStr, ValidationError

from app.auth.fastapi_users_instance import current_active_user, get_current_manager
from app.auth.models import User
from app.meetings.dependencies import MeetingServiceDep, current_meeting
from app.meetings.exceptions import (
    AlreadyParticipantError,
    MeetingDoesNotExistError,
    OverlappingMeetingError,
)
from app.meetings.models import Meeting
from app.meetings.schemas import MeetingCreate, MeetingFilters
from app.templates import templates

router = APIRouter(prefix="/meetings")

MEETING_LIST_PAGE_ROUTE_NAME = "meetings:list_page"
MEETING_DETAIL_PAGE_ROUTE_NAME = "meetings:detail_page"
MEETING_CREATE_PAGE_ROUTE_NAME = "meetings:create_page"
MEETING_CREATE_ROUTE_NAME = "create_meeting"
MEETING_DELETE_ROUTE_NAME = "delete_meeting"
MEETING_ADD_PARTICIPANT_ROUTE_NAME = "add_meeting_participant"
MEETING_REMOVE_PARTICIPANT_ROUTE_NAME = "remove_meeting_participant"
MEETING_MY_PAGE_ROUTE_NAME = "meetings:my_meetings_page"


@router.get("/", name=MEETING_LIST_PAGE_ROUTE_NAME)
async def meetings_list_page(
    filters: Annotated[MeetingFilters, Query()],
    user: Annotated[User, Depends(current_active_user)],
    meeting_service: MeetingServiceDep,
    request: Request,
):
    meetings = await meeting_service.get_meetings_list(filters)

    return templates.TemplateResponse(
        request=request,
        name="meetings/list.html",
        context={
            "title": "Meetings",
            "current_user": user,
            "meetings": meetings,
            "filters": filters,
        },
    )


@router.get("/my", name=MEETING_MY_PAGE_ROUTE_NAME)
async def my_meetings_page(
    filters: Annotated[MeetingFilters, Query()],
    user: Annotated[User, Depends(current_active_user)],
    meeting_service: MeetingServiceDep,
    request: Request,
):
    meetings = await meeting_service.get_user_meetings(user, filters)

    return templates.TemplateResponse(
        request=request,
        name="meetings/my.html",
        context={
            "title": "My Meetings",
            "current_user": user,
            "meetings": meetings,
            "filters": filters,
        },
    )


@router.get("/create", name=MEETING_CREATE_PAGE_ROUTE_NAME)
async def meetings_create_page(
    user: Annotated[User, Depends(get_current_manager)],
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="meetings/create.html",
        context={
            "title": "Create Meeting",
            "current_user": user,
        },
    )


@router.post("/create", name=MEETING_CREATE_ROUTE_NAME)
async def create_meeting(
    start_time: Annotated[datetime, Form()],
    end_time: Annotated[datetime, Form()],
    user_timezone: Annotated[str, Form()],
    user: Annotated[User, Depends(get_current_manager)],
    meeting_service: MeetingServiceDep,
    request: Request,
):
    user_tz = pytz.timezone(user_timezone)
    try:
        create_data = MeetingCreate(
            start_time=user_tz.localize(start_time).astimezone(UTC),
            end_time=user_tz.localize(end_time).astimezone(UTC),
        )
    except ValidationError as e:
        return templates.TemplateResponse(
            request=request,
            name="meetings/create.html",
            context={
                "title": "Create Meeting",
                "current_user": user,
                "error": e,
            },
        )

    try:
        meeting = await meeting_service.create_meeting(create_data, user)
        await meeting_service.uow.flush()
    except OverlappingMeetingError as e:
        return templates.TemplateResponse(
            request=request,
            name="meetings/create.html",
            context={
                "title": "Create Meeting",
                "current_user": user,
                "create_data": create_data,
                "error": e.message,
            },
        )

    return RedirectResponse(
        request.url_for(MEETING_DETAIL_PAGE_ROUTE_NAME, meeting_id=meeting.id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/{meeting_id}", name=MEETING_DETAIL_PAGE_ROUTE_NAME)
async def meetings_detail_page(
    meeting: Annotated[
        Meeting, Depends(current_meeting(current_active_user, full=True))
    ],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="meetings/detail.html",
        context={
            "title": f"Meeting {meeting.id}",
            "current_user": user,
            "meeting": meeting,
        },
    )


@router.post("/{meeting_id}/delete", name=MEETING_DELETE_ROUTE_NAME)
async def delete_meeting(
    meeting: Annotated[
        Meeting, Depends(current_meeting(current_active_user, author=True))
    ],
    meeting_service: MeetingServiceDep,
    request: Request,
):
    await meeting_service.delete_meeting(meeting)

    return RedirectResponse(
        request.url_for(MEETING_LIST_PAGE_ROUTE_NAME),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/{meeting_id}/add_participant", name=MEETING_ADD_PARTICIPANT_ROUTE_NAME)
async def add_meeting_participant(
    user_email: Annotated[EmailStr, Form()],
    meeting: Annotated[Meeting, Depends(current_meeting(get_current_manager))],
    user: Annotated[User, Depends(get_current_manager)],
    meeting_service: MeetingServiceDep,
    request: Request,
):
    error = None
    try:
        await meeting_service.add_participant(meeting, user_email)
    except UserNotExists:
        error = "User with the given email does not exist"
    except AlreadyParticipantError as e:
        error = e.message

    try:
        meeting = await meeting_service.get_meeting_by_id(meeting.id, full=True)
    except MeetingDoesNotExistError:
        return RedirectResponse(
            request.url_for(MEETING_LIST_PAGE_ROUTE_NAME),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return templates.TemplateResponse(
        request=request,
        name="meetings/detail.html",
        context={
            "title": f"Meeting {meeting.id}",
            "current_user": user,
            "meeting": meeting,
            "user_email": user_email,
            "error": error,
        },
    )


@router.post(
    "/{meeting_id}/remove_participant/{user_id}",
    name=MEETING_REMOVE_PARTICIPANT_ROUTE_NAME,
)
async def remove_meeting_participant(
    user_id: int,
    meeting: Annotated[Meeting, Depends(current_meeting(get_current_manager))],
    meeting_service: MeetingServiceDep,
    request: Request,
):
    with suppress(UserNotExists):
        await meeting_service.remove_participant(meeting, user_id)

    return RedirectResponse(
        request.url_for(MEETING_DETAIL_PAGE_ROUTE_NAME, meeting_id=meeting.id),
        status_code=status.HTTP_303_SEE_OTHER,
    )
