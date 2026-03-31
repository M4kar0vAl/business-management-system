from datetime import UTC, datetime, timedelta

import pytest
from fastapi import status

from app.auth.schemas import UserCreate
from app.tasks.routers.comments import CREATE_COMMENT_ROUTE_NAME
from app.tasks.schemas import CommentCreate, TaskCreate
from app.teams.schemas import TeamCreate
from tests.mixins import GetUrlMixin


@pytest.mark.integration
class TestCreateComment(GetUrlMixin):
    url_name = CREATE_COMMENT_ROUTE_NAME

    def get_url(self, task_id: int):
        return super().get_url(task_id=task_id)

    @property
    def _some_deadline(self) -> datetime:
        return datetime.now(UTC) + timedelta(minutes=10)

    async def test_create_comment(
        self,
        async_client,
        comment_repository,
        create_team,
        create_task,
        create_user,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        team = await create_team(TeamCreate(name="team"), members=[user])
        task = await create_task(
            TaskCreate(
                description="asfas", deadline=self._some_deadline, team_id=team.id
            ),
            author=user,
        )

        response = await async_client.post(
            self.get_url(task.id),
            json=CommentCreate(text="comment").model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()

        created_comment = await comment_repository.get_by_id(data["id"])
        assert created_comment is not None
        assert created_comment.text == data["text"]

    async def test_create_comment_unauthenticated(
        self, async_client, create_team, create_task, create_user
    ):
        user, _ = await create_user(
            UserCreate(email="user@example.com", password="Pass!234")
        )
        team = await create_team(TeamCreate(name="team"), members=[user])
        task = await create_task(
            TaskCreate(
                description="asfas", deadline=self._some_deadline, team_id=team.id
            ),
            author=user,
        )

        response = await async_client.post(
            self.get_url(task.id), json=CommentCreate(text="comment").model_dump()
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_comment_user_inactive(
        self,
        async_client,
        create_team,
        create_task,
        create_user,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", is_active=False),
            authenticate=True,
        )
        team = await create_team(TeamCreate(name="team"), members=[user])
        task = await create_task(
            TaskCreate(
                description="asfas", deadline=self._some_deadline, team_id=team.id
            ),
            author=user,
        )

        response = await async_client.post(
            self.get_url(task.id),
            json=CommentCreate(text="comment").model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_comment_task_does_not_exist(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )

        response = await async_client.post(
            self.get_url(0),
            json=CommentCreate(text="comment").model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_comment_user_not_in_task_team(
        self,
        async_client,
        session,
        create_team,
        task_repository,
        create_user,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        team = await create_team(TeamCreate(name="team"))
        task = await task_repository.create(
            TaskCreate(
                description="asfas", deadline=self._some_deadline, team_id=team.id
            ),
            team=team,
            author=user,
        )
        await session.flush()

        response = await async_client.post(
            self.get_url(task.id),
            json=CommentCreate(text="comment").model_dump(),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
