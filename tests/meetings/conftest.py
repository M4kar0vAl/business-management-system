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
async def create_meeting(meeting_service, meeting_repository):
    async def _create_meeting(
        meeting: MeetingCreate, user: User, participants: list[User] | None = None
    ):
        db_meeting = await meeting_service.create_meeting(meeting, user)
        participants = participants or []
        await meeting_service.uow.flush()

        for participant in participants:
            await meeting_repository.add_participant(db_meeting, participant)

        return db_meeting

    return _create_meeting
