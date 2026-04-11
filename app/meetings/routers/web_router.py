from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.auth.fastapi_users_instance import current_active_user
from app.auth.models import User
from app.meetings.dependencies import MeetingServiceDep
from app.meetings.schemas import MeetingFilters
from app.templates import templates

router = APIRouter(prefix="/meetings")

MEETING_LIST_PAGE_ROUTE_NAME = "meetings:list_page"


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
