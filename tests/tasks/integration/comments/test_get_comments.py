import json
from datetime import UTC, datetime, timedelta

from fastapi import status

from app.auth.schemas import UserCreate
from app.tasks.routers.comments import GET_COMMENTS_ROUTE_NAME
from app.tasks.schemas import CommentCreate, CommentRead, TaskCreate
from app.teams.schemas import TeamCreate
from tests.mixins import GetUrlMixin


class TestGetComments(GetUrlMixin):
    url_name = GET_COMMENTS_ROUTE_NAME

    def get_url(self, task_id: int):
        return super().get_url(task_id=task_id)

    @property
    def _some_deadline(self) -> datetime:
        return datetime.now(UTC) + timedelta(minutes=10)

    async def test_get_comments(
        self,
        async_client,
        create_team,
        create_user,
        create_task,
        create_comment,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        team = await create_team(TeamCreate(name="team1"), members=[user])
        task = await create_task(
            TaskCreate(
                description="afsaf", deadline=self._some_deadline, team_id=team.id
            ),
            author=user,
        )
        task2 = await create_task(
            TaskCreate(
                description="dgas", deadline=self._some_deadline, team_id=team.id
            ),
            author=user,
        )
        comment1 = await create_comment(
            CommentCreate(text="asfa"), task=task, author=user
        )
        comment2 = await create_comment(
            CommentCreate(text="asgds"), task=task, author=user
        )
        comment3 = await create_comment(
            CommentCreate(text="asgfdgsgds"), task=task2, author=user
        )

        response = await async_client.get(
            self.get_url(task.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert (
            json.loads(CommentRead.model_validate(comment1).model_dump_json()) in data
        )
        assert (
            json.loads(CommentRead.model_validate(comment2).model_dump_json()) in data
        )
        assert (
            json.loads(CommentRead.model_validate(comment3).model_dump_json())
            not in data
        )

    async def test_get_comments_unauthenticated(
        self, async_client, create_team, create_user, create_task
    ):
        user, _ = await create_user(
            UserCreate(email="user@example.com", password="Pass!234")
        )
        team = await create_team(TeamCreate(name="team"), members=[user])
        task = await create_task(
            TaskCreate(
                description="afsaf", deadline=self._some_deadline, team_id=team.id
            ),
            author=user,
        )
        response = await async_client.get(self.get_url(task.id))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_comments_inactive(
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
        team = await create_team(TeamCreate(name="team1"), members=[user])
        task = await create_task(
            TaskCreate(
                description="afsaf", deadline=self._some_deadline, team_id=team.id
            ),
            author=user,
        )

        response = await async_client.get(
            self.get_url(task.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_comments_task_not_found(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )

        response = await async_client.get(
            self.get_url(0), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_comments_user_not_a_member(
        self,
        async_client,
        create_team,
        create_user,
        task_repository,
        session,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        team = await create_team(TeamCreate(name="team1"))
        task = await task_repository.create(
            TaskCreate(
                description="afsaf", deadline=self._some_deadline, team_id=team.id
            ),
            team=team,
            author=user,
        )
        await session.flush()

        response = await async_client.get(
            self.get_url(task.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
