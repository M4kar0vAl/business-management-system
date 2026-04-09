import json
from datetime import UTC, datetime, timedelta

from fastapi import status

from app.auth.schemas import UserCreate
from app.tasks.routers.api.tasks import GET_ASSIGNED_TASKS_ROUTE_NAME
from app.tasks.schemas import TaskCreate, TaskReadFull
from app.teams.schemas import TeamCreate
from tests.mixins import GetUrlMixin


class TestGetAssignedTasks(GetUrlMixin):
    url_name = GET_ASSIGNED_TASKS_ROUTE_NAME

    @property
    def _some_deadline(self) -> datetime:
        return datetime.now(UTC) + timedelta(minutes=10)

    async def test_get_assigned_tasks(
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
                email="user@example.com",
                password="Pass!234",
            ),
            authenticate=True,
        )
        team = await create_team(TeamCreate(name="team"), members=[user])
        task_create = TaskCreate(
            description="asfjsa", deadline=self._some_deadline, team_id=team.id
        )
        task1 = await create_task(
            task_create,
            author=user,
            assignee=user,
        )
        task2 = await create_task(
            task_create,
            author=user,
            assignee=user,
        )

        response = await async_client.get(
            self.get_url(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK

        expected_task1 = await task_repository.get_by_id_full(task1.id)
        expected_task2 = await task_repository.get_by_id_full(task2.id)
        assert (
            json.loads(TaskReadFull.model_validate(expected_task1).model_dump_json())
            in response.json()
        )
        assert (
            json.loads(TaskReadFull.model_validate(expected_task2).model_dump_json())
            in response.json()
        )

    async def test_get_assigned_tasks_unauthenticated(
        self, async_client, create_user, create_team, create_task
    ):
        user, _ = await create_user(
            UserCreate(email="user@example.com", password="Pass!234")
        )
        team = await create_team(TeamCreate(name="team"), members=[user])
        await create_task(
            TaskCreate(
                description="asfjsa", deadline=self._some_deadline, team_id=team.id
            ),
            author=user,
            assignee=user,
        )

        response = await async_client.get(self.get_url())

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_assigned_tasks_inactive(
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
        await create_task(
            TaskCreate(
                description="asfjsa", deadline=self._some_deadline, team_id=team.id
            ),
            author=user,
            assignee=user,
        )

        response = await async_client.get(
            self.get_url(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_assigned_tasks_user_not_a_member_of_team(
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
                email="user@example.com",
                password="Pass!234",
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
        task.assignee = user
        await session.flush()

        response = await async_client.get(
            self.get_url(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK

        expected_task = await task_repository.get_by_id_full(task.id)
        assert (
            json.loads(TaskReadFull.model_validate(expected_task).model_dump_json())
            in response.json()
        )
