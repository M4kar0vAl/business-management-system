from datetime import UTC, datetime, timedelta

import pytest
from fastapi import status

from app.auth.models import Role
from app.auth.schemas import UserCreate
from app.tasks.routers.tasks import ASSIGN_USER_TO_TASK_ROUTE_NAME
from app.tasks.schemas import TaskCreate
from app.teams.schemas import TeamCreate
from tests.mixins import GetUrlMixin


@pytest.mark.integration
class TestAssignUserToTask(GetUrlMixin):
    url_name = ASSIGN_USER_TO_TASK_ROUTE_NAME

    def get_url(self, task_id: int, assignee_id: int):
        return super().get_url(task_id=task_id, assignee_id=assignee_id)

    @property
    def _some_deadline(self) -> datetime:
        return datetime.now(UTC) + timedelta(minutes=10)

    async def test_assign_user_to_task(
        self,
        async_client,
        create_user,
        create_team,
        create_task,
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
        task = await create_task(
            TaskCreate(
                description="asfjsa", deadline=self._some_deadline, team_id=team.id
            ),
            author=user,
        )

        response = await async_client.post(
            self.get_url(task.id, user.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK

        updated_task = await task_repository.get_by_id(task.id)
        assert updated_task is not None
        assert updated_task.assignee_id == user.id

    async def test_assign_user_to_task_unauthenticated(
        self, async_client, create_user, create_team, create_task
    ):
        user, _ = await create_user(
            UserCreate(email="user@example.com", password="Pass!234")
        )
        team = await create_team(TeamCreate(name="team"), members=[user])
        task = await create_task(
            TaskCreate(
                description="asfjsa", deadline=self._some_deadline, team_id=team.id
            ),
            author=user,
        )

        response = await async_client.post(self.get_url(task.id, user.id))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_assign_user_to_task_inactive(
        self,
        async_client,
        create_user,
        create_team,
        create_task,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", is_active=False),
            authenticate=True,
        )
        team = await create_team(TeamCreate(name="team"), members=[user])
        task = await create_task(
            TaskCreate(
                description="asfjsa", deadline=self._some_deadline, team_id=team.id
            ),
            author=user,
        )

        response = await async_client.post(
            self.get_url(task.id, user.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_assign_user_to_task_non_manager(
        self,
        async_client,
        create_user,
        create_team,
        create_task,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        team = await create_team(TeamCreate(name="team"), members=[user])
        task = await create_task(
            TaskCreate(
                description="asfjsa", deadline=self._some_deadline, team_id=team.id
            ),
            author=user,
        )

        response = await async_client.post(
            self.get_url(task.id, user.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_assign_user_to_task_not_exists(
        self, async_client, create_user, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com", password="Pass!234", role=Role.MANAGER
            ),
            authenticate=True,
        )

        response = await async_client.post(
            self.get_url(0, user.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_assign_user_to_task_already_assigned(
        self,
        async_client,
        create_user,
        create_team,
        create_task,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com", password="Pass!234", role=Role.MANAGER
            ),
            authenticate=True,
        )
        team = await create_team(TeamCreate(name="team"), members=[user])
        task = await create_task(
            TaskCreate(
                description="asfjsa", deadline=self._some_deadline, team_id=team.id
            ),
            author=user,
            assignee=user,
        )

        response = await async_client.post(
            self.get_url(task.id, user.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_assign_user_to_task_assigner_not_a_member_of_team(
        self,
        async_client,
        session,
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
        team = await create_team(TeamCreate(name="team"))
        task = await task_repository.create(
            TaskCreate(
                description="asfjsa", deadline=self._some_deadline, team_id=team.id
            ),
            team=team,
            author=user,
        )
        await session.flush()

        response = await async_client.post(
            self.get_url(task.id, user.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_assign_user_to_task_assignee_not_a_member_of_team(
        self,
        async_client,
        session,
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
        assignee, _ = await create_user(
            UserCreate(email="assignee@example.com", password="Pass!234")
        )
        team = await create_team(TeamCreate(name="team"), members=[user])
        task = await task_repository.create(
            TaskCreate(
                description="asfjsa", deadline=self._some_deadline, team_id=team.id
            ),
            team=team,
            author=user,
        )
        await session.flush()

        response = await async_client.post(
            self.get_url(task.id, assignee.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
