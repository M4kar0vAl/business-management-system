import pytest

from app.teams.repositories import TeamRepository
from app.teams.schemas import TeamCreate
from app.teams.services import TeamService


@pytest.fixture
async def team_repository(session):
    return TeamRepository(session)


@pytest.fixture
async def team_service(uow, user_manager):
    return TeamService(uow, user_manager)


@pytest.fixture
async def create_team(team_service):

    async def _create_team(team_create: TeamCreate):
        return await team_service.create_team(team_create)

    return _create_team
