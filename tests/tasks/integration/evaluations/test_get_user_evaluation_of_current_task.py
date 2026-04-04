import json
from datetime import UTC, datetime, timedelta

from fastapi import status

from app.auth.models import Role
from app.auth.schemas import UserCreate
from app.tasks.routers.evaluations import EVALUATION_GET_OF_TASK_ROUTE_NAME
from app.tasks.schemas import EvaluationCreate, EvaluationRead, TaskCreate
from app.teams.schemas import TeamCreate
from tests.mixins import GetUrlMixin


class TestGetUserEvaluationOfCurrentTask(GetUrlMixin):
    url_name = EVALUATION_GET_OF_TASK_ROUTE_NAME

    def get_url(self, task_id: int):
        return super().get_url(task_id=task_id)

    @property
    def _some_deadline(self) -> datetime:
        return datetime.now(UTC) + timedelta(minutes=10)

    async def test_get_user_evaluation_of_task(
        self,
        async_client,
        create_user,
        create_team,
        create_task,
        create_evaluation,
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
                description="asfas",
                deadline=self._some_deadline,
                team_id=team.id,
            ),
            author=user,
        )
        evaluation = await create_evaluation(
            EvaluationCreate(value=3), task=task, author=user
        )

        response = await async_client.get(
            self.get_url(task.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data == json.loads(
            EvaluationRead.model_validate(evaluation).model_dump_json()
        )

    async def test_get_user_evaluation_of_task_unauthenticated(
        self, async_client, create_user, create_team, create_task
    ):
        user, _ = await create_user(
            UserCreate(
                email="user@example.com", password="Pass!234", role=Role.MANAGER
            ),
        )
        team = await create_team(TeamCreate(name="team"), members=[user])
        task = await create_task(
            TaskCreate(
                description="asfas",
                deadline=self._some_deadline,
                team_id=team.id,
            ),
            author=user,
        )

        response = await async_client.get(
            self.get_url(task.id),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_user_evaluation_of_task_inactive(
        self,
        async_client,
        create_user,
        create_team,
        create_task,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
                role=Role.MANAGER,
                is_active=False,
            ),
            authenticate=True,
        )
        team = await create_team(TeamCreate(name="team"), members=[user])
        task = await create_task(
            TaskCreate(
                description="asfas",
                deadline=self._some_deadline,
                team_id=team.id,
            ),
            author=user,
        )

        response = await async_client.get(
            self.get_url(task.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_user_evaluation_of_task_non_manager(
        self,
        async_client,
        create_user,
        create_team,
        create_task,
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
        task = await create_task(
            TaskCreate(
                description="asfas",
                deadline=self._some_deadline,
                team_id=team.id,
            ),
            author=user,
        )

        response = await async_client.get(
            self.get_url(task.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_user_evaluation_of_task_task_not_exists(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(
                email="user@example.com", password="Pass!234", role=Role.MANAGER
            ),
            authenticate=True,
        )

        response = await async_client.get(
            self.get_url(0),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_user_evaluation_of_task_evaluation_not_exists(
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
                description="asfas",
                deadline=self._some_deadline,
                team_id=team.id,
            ),
            author=user,
        )

        response = await async_client.get(
            self.get_url(task.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_get_user_evaluation_of_task_not_an_author_of_evaluation(
        self,
        async_client,
        create_user,
        create_team,
        create_task,
        create_evaluation,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com", password="Pass!234", role=Role.MANAGER
            ),
            authenticate=True,
        )
        another_user, _ = await create_user(
            UserCreate(
                email="user1@example.com",
                password="Pass!234",
            ),
        )
        team = await create_team(TeamCreate(name="team"), members=[user, another_user])
        task = await create_task(
            TaskCreate(
                description="asfas",
                deadline=self._some_deadline,
                team_id=team.id,
            ),
            author=user,
        )
        # evaluation by another user
        await create_evaluation(
            EvaluationCreate(value=3), task=task, author=another_user
        )

        response = await async_client.get(
            self.get_url(task.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    async def test_get_user_evaluation_of_task_user_not_in_task_team(
        self,
        async_client,
        task_repository,
        create_user,
        create_team,
        create_evaluation,
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
                description="asfas",
                deadline=self._some_deadline,
                team_id=team.id,
            ),
            team=team,
            author=user,
        )
        await create_evaluation(EvaluationCreate(value=3), task=task, author=user)

        response = await async_client.get(
            self.get_url(task.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
