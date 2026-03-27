import pytest

from app.auth.models import User
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
async def create_team(team_service, team_repository):

    async def _create_team(team_create: TeamCreate, members: list[User] | None = None):
        team = await team_service.create_team(team_create)
        members = members or []

        for member in members:
            await team_repository.assign_user_to_team(team, member)

        await team_service.uow.flush()
        return team

    return _create_team
