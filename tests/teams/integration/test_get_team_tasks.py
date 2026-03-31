import json
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import status

from app.auth.schemas import UserCreate
from app.tasks.schemas import TaskCreate
from app.tasks.schemas.tasks import TaskReadFull
from app.teams.routers import GET_TEAM_TASKS_ROUTE_NAME
from app.teams.schemas import TeamCreate
from tests.mixins import GetUrlMixin


@pytest.mark.integration
class TestGetTeamTasks(GetUrlMixin):
    url_name = GET_TEAM_TASKS_ROUTE_NAME

    def get_url(self, team_id: int):
        return super().get_url(team_id=team_id)

    @property
    def _some_deadline(self) -> datetime:
        return datetime.now(UTC) + timedelta(minutes=10)

    async def test_get_team_tasks(
        self,
        async_client,
        create_team,
        create_user,
        create_task,
        task_repository,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        user2, _ = await create_user(
            UserCreate(email="user1@example.com", password="Pass!234")
        )
        team1 = await create_team(TeamCreate(name="team1"), members=[user])
        team2 = await create_team(TeamCreate(name="team2"), members=[user2])
        task1 = await create_task(
            TaskCreate(
                description="afsaf", deadline=self._some_deadline, team_id=team1.id
            ),
            author=user,
        )
        task2 = await create_task(
            TaskCreate(
                description="asfg", deadline=self._some_deadline, team_id=team1.id
            ),
            author=user,
        )
        task3 = await create_task(
            TaskCreate(
                description="sfsdgsa", deadline=self._some_deadline, team_id=team2.id
            ),
            author=user2,
        )

        response = await async_client.get(
            self.get_url(team1.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        expected_task1 = await task_repository.get_by_id_full(task1.id)
        expected_task2 = await task_repository.get_by_id_full(task2.id)
        expected_task3 = await task_repository.get_by_id_full(task3.id)
        assert (
            json.loads(TaskReadFull.model_validate(expected_task1).model_dump_json())
            in data
        )
        assert (
            json.loads(TaskReadFull.model_validate(expected_task2).model_dump_json())
            in data
        )
        assert (
            json.loads(TaskReadFull.model_validate(expected_task3).model_dump_json())
            not in data
        )

    async def test_get_team_tasks_unauthenticated(self, async_client, create_team):
        team = await create_team(TeamCreate(name="team"))
        response = await async_client.get(self.get_url(team.id))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_team_tasks_inactive(
        self, async_client, create_user, create_team, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", is_active=False),
            authenticate=True,
        )
        team = await create_team(TeamCreate(name="team1"))

        response = await async_client.get(
            self.get_url(team.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_team_tasks_team_not_found(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )

        response = await async_client.get(
            self.get_url(0), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_team_tasks_user_not_a_member(
        self, async_client, create_team, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        team = await create_team(TeamCreate(name="team1"))

        response = await async_client.get(
            self.get_url(team.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
