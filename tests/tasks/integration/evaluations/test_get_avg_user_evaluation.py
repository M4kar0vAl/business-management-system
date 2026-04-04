from datetime import UTC, datetime, timedelta
from functools import reduce

from fastapi import status

from app.auth.schemas import UserCreate
from app.tasks.models import TaskStatus
from app.tasks.routers.evaluations import EVALUATION_GET_USER_AVG_EVALUATIONS_ROUTE_NAME
from app.tasks.schemas import EvaluationCreate, TaskCreate
from app.teams.schemas import TeamCreate
from tests.mixins import GetUrlMixin


class TestGetAvgUserEvaluation(GetUrlMixin):
    url_name = EVALUATION_GET_USER_AVG_EVALUATIONS_ROUTE_NAME

    @property
    def _some_deadline(self) -> datetime:
        return datetime.now(UTC) + timedelta(minutes=10)

    async def test_get_avg_user_evaluation(
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
        task_create = TaskCreate(
            description="asfas",
            deadline=self._some_deadline,
            status=TaskStatus.DONE,
            team_id=team.id,
        )
        task_assigned1 = await create_task(
            task_create,
            author=user,
            assignee=user,
        )
        task_assigned2 = await create_task(
            task_create,
            author=another_user,
            assignee=user,
        )
        task_not_assigned = await create_task(
            task_create,
            author=user,
        )
        evaluation1 = await create_evaluation(
            EvaluationCreate(value=1), task=task_assigned1, author=another_user
        )
        evaluation2 = await create_evaluation(
            EvaluationCreate(value=2), task=task_assigned2, author=another_user
        )
        await create_evaluation(
            EvaluationCreate(value=3), task=task_not_assigned, author=user
        )

        response = await async_client.get(
            self.get_url(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        evaluations = (evaluation1, evaluation2)
        assert data == reduce(
            lambda acc, cur: acc + cur.value, evaluations, initial=0
        ) / len(evaluations)

    async def test_get_avg_user_evaluation_unauthenticated(self, async_client):
        response = await async_client.get(
            self.get_url(),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_avg_user_evaluation_inactive(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
                is_active=False,
            ),
            authenticate=True,
        )

        response = await async_client.get(
            self.get_url(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_avg_user_evaluation_for_period(
        self,
        async_client,
        session,
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
        task_create = TaskCreate(
            description="asfas",
            deadline=self._some_deadline,
            status=TaskStatus.DONE,
            team_id=team.id,
        )
        task_assigned1 = await create_task(
            task_create,
            author=user,
            assignee=user,
        )
        task_assigned2 = await create_task(
            task_create,
            author=another_user,
            assignee=user,
        )
        task_assigned3 = await create_task(
            task_create,
            author=user,
            assignee=user,
        )
        evaluation1 = await create_evaluation(
            EvaluationCreate(value=1), task=task_assigned1, author=another_user
        )
        evaluation2 = await create_evaluation(
            EvaluationCreate(value=2), task=task_assigned2, author=another_user
        )
        evaluation3 = await create_evaluation(
            EvaluationCreate(value=3), task=task_assigned3, author=another_user
        )
        now = datetime.now(UTC)
        yesterday = now - timedelta(days=1)
        two_days_ago = now - timedelta(days=2)
        three_days_ago = now - timedelta(days=3)
        evaluation1.created_at = yesterday
        evaluation2.created_at = two_days_ago
        evaluation3.created_at = three_days_ago
        await session.flush()

        response = await async_client.get(
            self.get_url(),
            params={"start": three_days_ago.date(), "end": two_days_ago.date()},
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        evaluations = (evaluation2, evaluation3)
        assert data == reduce(
            lambda acc, cur: acc + cur.value, evaluations, initial=0
        ) / len(evaluations)

    async def test_get_avg_user_evaluation_for_period_start_later_than_end(
        self,
        async_client,
        create_user,
        get_authorization_header,
    ):
        _, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
            ),
            authenticate=True,
        )
        now = datetime.now(UTC)
        yesterday = now - timedelta(days=1)
        two_days_ago = now - timedelta(days=2)

        response = await async_client.get(
            self.get_url(),
            params={"start": yesterday.date(), "end": two_days_ago.date()},
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_get_avg_user_evaluation_for_task(
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
        task_create = TaskCreate(
            description="asfas",
            deadline=self._some_deadline,
            status=TaskStatus.DONE,
            team_id=team.id,
        )
        task_assigned1 = await create_task(
            task_create,
            author=user,
            assignee=user,
        )
        task_assigned2 = await create_task(
            task_create,
            author=another_user,
            assignee=user,
        )
        evaluation1 = await create_evaluation(
            EvaluationCreate(value=1), task=task_assigned1, author=another_user
        )
        await create_evaluation(
            EvaluationCreate(value=2), task=task_assigned2, author=another_user
        )

        response = await async_client.get(
            self.get_url(),
            params={"task_id": task_assigned1.id},
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data == evaluation1.value
