import json
from datetime import UTC, datetime, timedelta

from fastapi import status

from app.auth.schemas import UserCreate
from app.tasks.routers.api.tasks import GET_TASKS_CALENDAR_ROUTE_NAME
from app.tasks.schemas import TaskCreate, TaskRead
from app.teams.schemas import TeamCreate
from tests.mixins import GetUrlMixin


class TestGetTasksCalendar(GetUrlMixin):
    url_name = GET_TASKS_CALENDAR_ROUTE_NAME

    @property
    def _some_deadline(self) -> datetime:
        return datetime.now(UTC) + timedelta(minutes=10)

    async def test_get_tasks_calendar(
        self,
        async_client,
        session,
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
        another_team = await create_team(TeamCreate(name="another_team"))
        task_create = TaskCreate(
            description="asfjsa", deadline=self._some_deadline, team_id=team.id
        )
        # matches filters
        task1 = await create_task(
            task_create,
            author=user,
            assignee=user,
        )
        # deadline out of range
        task2 = await create_task(
            task_create.model_copy(
                update={"deadline": self._some_deadline + timedelta(days=1)}
            ),
            author=user,
            assignee=user,
        )
        # user not assignee
        task3 = await create_task(
            task_create,
            author=user,
        )
        # another team
        task4 = await task_repository.create(
            task_create.model_copy(update={"team_id": another_team.id}),
            team=another_team,
            author=user,
        )
        task4.assignee = user
        await session.flush()

        params = {
            "start": self._some_deadline - timedelta(hours=12),
            "end": self._some_deadline + timedelta(hours=12),
            "team_id": team.id,
            "assignee_id": user.id,
        }

        response = await async_client.get(
            self.get_url(),
            params=params,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK

        expected_task1 = await task_repository.get_by_id(task1.id)
        expected_task2 = await task_repository.get_by_id(task2.id)
        expected_task3 = await task_repository.get_by_id(task3.id)
        expected_task4 = await task_repository.get_by_id(task4.id)
        assert (
            json.loads(TaskRead.model_validate(expected_task1).model_dump_json())
            in response.json()
        )
        assert (
            json.loads(TaskRead.model_validate(expected_task2).model_dump_json())
            not in response.json()
        )
        assert (
            json.loads(TaskRead.model_validate(expected_task3).model_dump_json())
            not in response.json()
        )
        assert (
            json.loads(TaskRead.model_validate(expected_task4).model_dump_json())
            not in response.json()
        )

    async def test_get_tasks_calendar_unauthenticated(
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
        params = {
            "start": self._some_deadline - timedelta(hours=12),
            "end": self._some_deadline + timedelta(hours=12),
        }

        response = await async_client.get(self.get_url(), params=params)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_tasks_calendar_inactive(
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
        params = {
            "start": self._some_deadline - timedelta(hours=12),
            "end": self._some_deadline + timedelta(hours=12),
        }

        response = await async_client.get(
            self.get_url(),
            params=params,
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
