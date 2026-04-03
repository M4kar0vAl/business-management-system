from datetime import UTC, datetime, timedelta

from fastapi import status

from app.auth.models import Role
from app.auth.schemas import UserCreate
from app.tasks.models import TaskStatus
from app.tasks.routers.evaluations import EVALUATION_UPDATE_ROUTE_NAME
from app.tasks.schemas import EvaluationCreate, EvaluationUpdate, TaskCreate
from app.teams.schemas import TeamCreate
from tests.mixins import GetUrlMixin


class TestUpdateEvaluation(GetUrlMixin):
    url_name = EVALUATION_UPDATE_ROUTE_NAME

    def get_url(self, task_id: int, evaluation_id: int) -> str:
        return super().get_url(task_id=task_id, evaluation_id=evaluation_id)

    @property
    def _some_deadline(self) -> datetime:
        return datetime.now(UTC) + timedelta(minutes=10)

    async def test_update_evaluation(
        self,
        async_client,
        create_user,
        create_team,
        create_task,
        create_evaluation,
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
        evaluation = await create_evaluation(
            EvaluationCreate(value=1), task=task, author=user
        )
        evaluation_update = EvaluationUpdate(value=3)

        response = await async_client.patch(
            self.get_url(task.id, evaluation.id),
            json=evaluation_update.model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        updated_evaluation = await evaluations_repository.get_by_id(data["id"])
        assert updated_evaluation is not None
        assert updated_evaluation.value == data["value"]
        assert updated_evaluation.value == evaluation_update.value

    async def test_update_evaluation_unauthenticated(
        self, async_client, create_user, create_team, create_task, create_evaluation
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
        evaluation = await create_evaluation(
            EvaluationCreate(value=1), task=task, author=user
        )

        response = await async_client.patch(
            self.get_url(task.id, evaluation.id),
            json=EvaluationUpdate(value=3).model_dump(),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_evaluation_inactive(
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
        evaluation = await create_evaluation(
            EvaluationCreate(value=1), task=task, author=user
        )

        response = await async_client.patch(
            self.get_url(task.id, evaluation.id),
            json=EvaluationUpdate(value=3).model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_evaluation_non_manager(
        self,
        async_client,
        create_user,
        create_team,
        create_task,
        create_evaluation,
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
        evaluation = await create_evaluation(
            EvaluationCreate(value=1), task=task, author=user
        )

        response = await async_client.patch(
            self.get_url(task.id, evaluation.id),
            json=EvaluationUpdate(value=3).model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_evaluation_task_not_exists(
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
        evaluation = await create_evaluation(
            EvaluationCreate(value=1), task=task, author=user
        )

        response = await async_client.patch(
            self.get_url(0, evaluation.id),
            json=EvaluationUpdate(value=3).model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_evaluation_evaluation_not_exists(
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
                status=TaskStatus.DONE,
                team_id=team.id,
            ),
            author=user,
        )

        response = await async_client.patch(
            self.get_url(task.id, 0),
            json=EvaluationUpdate(value=3).model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_evaluation_user_not_in_task_team(
        self,
        async_client,
        session,
        create_user,
        create_team,
        create_evaluation,
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
        evaluation = await create_evaluation(
            EvaluationCreate(value=1), task=task, author=user
        )

        response = await async_client.patch(
            self.get_url(task.id, evaluation.id),
            json=EvaluationUpdate(value=3).model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_update_evaluation_task_not_done(
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
                status=TaskStatus.IN_PROGRESS,
                team_id=team.id,
            ),
            author=user,
        )
        evaluation = await create_evaluation(
            EvaluationCreate(value=1), task=task, author=user
        )

        response = await async_client.patch(
            self.get_url(task.id, evaluation.id),
            json=EvaluationUpdate(value=3).model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_update_evaluation_not_an_evaluation_author(
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
                email="user1@example.com", password="Pass!234", role=Role.MANAGER
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
        evaluation = await create_evaluation(
            EvaluationCreate(value=1), task=task, author=another_user
        )

        response = await async_client.patch(
            self.get_url(task.id, evaluation.id),
            json=EvaluationUpdate(value=3).model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_evaluation_not_belongs_to_task(
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
        another_task = await create_task(
            TaskCreate(
                description="asfas",
                deadline=self._some_deadline,
                status=TaskStatus.DONE,
                team_id=team.id,
            ),
            author=user,
        )
        evaluation = await create_evaluation(
            EvaluationCreate(value=1), task=task, author=user
        )

        response = await async_client.patch(
            self.get_url(another_task.id, evaluation.id),
            json=EvaluationUpdate(value=3).model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
