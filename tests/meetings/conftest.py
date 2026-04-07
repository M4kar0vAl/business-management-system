import pytest

from app.auth.models import User
from app.meetings.repositories import MeetingRepository
from app.meetings.schemas import MeetingCreate
from app.meetings.services import MeetingService


@pytest.fixture
async def meeting_repository(session):
    return MeetingRepository(session)


@pytest.fixture
async def meeting_service(uow, user_manager):
    return MeetingService(uow, user_manager)


@pytest.fixture
async def create_meeting(meeting_service):
    async def _create_meeting(meeting: MeetingCreate, user: User):
        db_meeting = await meeting_service.create_meeting(meeting, user)
        await meeting_service.uow.flush()
        return db_meeting

    return _create_meeting
