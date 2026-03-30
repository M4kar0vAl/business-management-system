import json
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import status

from app.auth.models import Role
from app.auth.schemas import UserCreate
from app.tasks.routers.tasks import TASK_CREATE_ROUTE_NAME
from app.tasks.schemas import TaskCreate
from app.teams.schemas import TeamCreate
from tests.mixins import GetUrlMixin


@pytest.mark.integration
class TestCreateTask(GetUrlMixin):
    url_name = TASK_CREATE_ROUTE_NAME

    @property
    def _some_deadline(self) -> datetime:
        return datetime.now(UTC) + timedelta(minutes=10)

    async def test_create_task(
        self,
        async_client,
        create_user,
        create_team,
        task_repository,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com", password="Pass!234", role=Role.MANAGER
            ),
            authenticate=True,
        )
        team = await create_team(TeamCreate(name="team"), members=[user])
        task_create = TaskCreate(
            description="asfjsa", deadline=self._some_deadline, team_id=team.id
        )

        response = await async_client.post(
            self.get_url(),
            json=json.loads(task_create.model_dump_json()),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert "id" in data

        created_task = await task_repository.get_by_id(data["id"])
        assert created_task is not None

        for field, value in task_create.model_dump().items():
            assert getattr(created_task, field) == value

    async def test_create_task_unauthenticated(
        self, async_client, create_user, create_team
    ):
        user, _ = await create_user(
            UserCreate(email="user@example.com", password="Pass!234")
        )
        team = await create_team(TeamCreate(name="team"), members=[user])

        response = await async_client.post(
            self.get_url(),
            json=TaskCreate(
                description="asfjsa", deadline=self._some_deadline, team_id=team.id
            ).model_dump_json(),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_task_inactive(
        self, async_client, create_user, create_team, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", is_active=False),
            authenticate=True,
        )
        team = await create_team(TeamCreate(name="team"), members=[user])

        response = await async_client.post(
            self.get_url(),
            json=TaskCreate(
                description="asfjsa", deadline=self._some_deadline, team_id=team.id
            ).model_dump_json(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_task_non_manager(
        self, async_client, create_user, create_team, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        team = await create_team(TeamCreate(name="team"), members=[user])

        response = await async_client.post(
            self.get_url(),
            json=TaskCreate(
                description="asfjsa", deadline=self._some_deadline, team_id=team.id
            ).model_dump_json(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_create_task_team_does_not_exist(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(
                email="user@example.com", password="Pass!234", role=Role.MANAGER
            ),
            authenticate=True,
        )

        response = await async_client.post(
            self.get_url(),
            json=json.loads(
                TaskCreate(
                    description="asfjsa", deadline=self._some_deadline, team_id=1
                ).model_dump_json()
            ),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_task_user_not_a_member_of_team(
        self, async_client, create_user, create_team, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(
                email="user@example.com", password="Pass!234", role=Role.MANAGER
            ),
            authenticate=True,
        )
        team = await create_team(TeamCreate(name="team"))

        response = await async_client.post(
            self.get_url(),
            json=json.loads(
                TaskCreate(
                    description="asfjsa", deadline=self._some_deadline, team_id=team.id
                ).model_dump_json()
            ),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_create_task_deadline_not_in_future(
        self,
        async_client,
        create_user,
        create_team,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com", password="Pass!234", role=Role.MANAGER
            ),
            authenticate=True,
        )
        team = await create_team(TeamCreate(name="team"), members=[user])
        task_create = TaskCreate.model_construct(
            description="asfjsa", deadline=datetime.now(UTC), team_id=team.id
        )

        response = await async_client.post(
            self.get_url(),
            json=json.loads(task_create.model_dump_json()),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
