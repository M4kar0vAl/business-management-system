from datetime import UTC, datetime, timedelta

from fastapi import status

from app.auth.models import Role
from app.auth.schemas import UserCreate
from app.tasks.models import TaskStatus
from app.tasks.routers.api.evaluations import EVALUATION_CREATE_ROUTE_NAME
from app.tasks.schemas import EvaluationCreate, TaskCreate
from app.teams.schemas import TeamCreate
from tests.mixins import GetUrlMixin


class TestCreateEvaluation(GetUrlMixin):
    url_name = EVALUATION_CREATE_ROUTE_NAME

    def get_url(self, task_id: int):
        return super().get_url(task_id=task_id)

    @property
    def _some_deadline(self) -> datetime:
        return datetime.now(UTC) + timedelta(minutes=10)

    async def test_create_evaluation(
        self,
        async_client,
        create_user,
        create_team,
        create_task,
        evaluations_repository,
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
                status=TaskStatus.DONE,
                team_id=team.id,
            ),
            author=user,
        )
        evaluation_create = EvaluationCreate(value=3)

        response = await async_client.post(
            self.get_url(task.id),
            json=evaluation_create.model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()

        created_evaluation = await evaluations_repository.get_by_id(data["id"])
        assert created_evaluation is not None
        assert created_evaluation.value == data["value"]
        assert created_evaluation.value == evaluation_create.value
        assert created_evaluation.author_id == user.id
        assert created_evaluation.task_id == task.id

    async def test_create_evaluation_unauthenticated(
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
                status=TaskStatus.DONE,
                team_id=team.id,
            ),
            author=user,
        )

        response = await async_client.post(
            self.get_url(task.id),
            json=EvaluationCreate(value=3).model_dump(),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_evaluation_inactive(
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
                status=TaskStatus.DONE,
                team_id=team.id,
            ),
            author=user,
        )

        response = await async_client.post(
            self.get_url(task.id),
            json=EvaluationCreate(value=3).model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_evaluation_non_manager(
        self,
        async_client,
        create_user,
        create_team,
        create_task,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"),
            authenticate=True,
        )
        team = await create_team(TeamCreate(name="team"), members=[user])
        task = await create_task(
            TaskCreate(
                description="asfas",
                deadline=self._some_deadline,
                status=TaskStatus.DONE,
                team_id=team.id,
            ),
            author=user,
        )

        response = await async_client.post(
            self.get_url(task.id),
            json=EvaluationCreate(value=3).model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_create_evaluation_task_not_exists(
        self,
        async_client,
        create_user,
        get_authorization_header,
    ):
        _, token = await create_user(
            UserCreate(
                email="user@example.com", password="Pass!234", role=Role.MANAGER
            ),
            authenticate=True,
        )

        response = await async_client.post(
            self.get_url(0),
            json=EvaluationCreate(value=3).model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_evaluation_user_not_in_task_team(
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
                description="asfas",
                deadline=self._some_deadline,
                status=TaskStatus.DONE,
                team_id=team.id,
            ),
            team=team,
            author=user,
        )
        await session.flush()

        response = await async_client.post(
            self.get_url(task.id),
            json=EvaluationCreate(value=3).model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_create_evaluation_task_not_done(
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
                status=TaskStatus.IN_PROGRESS,
                team_id=team.id,
            ),
            author=user,
        )

        response = await async_client.post(
            self.get_url(task.id),
            json=EvaluationCreate(value=3).model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_create_evaluation_already_exists(
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
                status=TaskStatus.DONE,
                team_id=team.id,
            ),
            author=user,
        )
        evaluation_create = EvaluationCreate(value=3)
        await create_evaluation(evaluation_create, task=task, author=user)

        response = await async_client.post(
            self.get_url(task.id),
            json=evaluation_create.model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
