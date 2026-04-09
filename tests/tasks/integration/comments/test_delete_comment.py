from datetime import UTC, datetime, timedelta

from fastapi import status

from app.auth.schemas import UserCreate
from app.tasks.routers.api.comments import DELETE_COMMENT_ROUTE_NAME
from app.tasks.schemas import CommentCreate, TaskCreate
from app.teams.schemas import TeamCreate
from tests.mixins import GetUrlMixin


class TestDeleteComment(GetUrlMixin):
    url_name = DELETE_COMMENT_ROUTE_NAME

    def get_url(self, task_id: int, comment_id: int):
        return super().get_url(task_id=task_id, comment_id=comment_id)

    @property
    def _some_deadline(self) -> datetime:
        return datetime.now(UTC) + timedelta(minutes=10)

    async def test_delete_comment(
        self,
        async_client,
        create_user,
        create_team,
        create_task,
        create_comment,
        get_authorization_header,
        comment_repository,
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
        comment = await create_comment(CommentCreate(text="comment"), task, user)

        response = await async_client.delete(
            self.get_url(task.id, comment.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        deleted_comment = await comment_repository.get_by_id(comment.id)
        assert deleted_comment is None

    async def test_delete_comment_unauthenticated(
        self, async_client, create_user, create_team, create_task, create_comment
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
        comment = await create_comment(CommentCreate(text="comment"), task, user)

        response = await async_client.delete(
            self.get_url(task.id, comment.id),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_delete_comment_inactive(
        self,
        async_client,
        create_user,
        create_team,
        create_task,
        create_comment,
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
        comment = await create_comment(CommentCreate(text="comment"), task, user)

        response = await async_client.delete(
            self.get_url(task.id, comment.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_delete_comment_comment_does_not_exist(
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
                description="asfas", deadline=self._some_deadline, team_id=team.id
            ),
            author=user,
        )

        response = await async_client.delete(
            self.get_url(task.id, 0),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_comment_task_does_not_exist(
        self,
        async_client,
        create_user,
        create_team,
        create_task,
        create_comment,
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
        comment = await create_comment(CommentCreate(text="comment"), task, user)

        response = await async_client.delete(
            self.get_url(0, comment.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_comment_user_not_member_of_a_task_team(
        self,
        async_client,
        task_repository,
        comment_repository,
        session,
        create_user,
        create_team,
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
        comment = await comment_repository.create(
            CommentCreate(text="comment"), user, task
        )
        await session.flush()

        response = await async_client.delete(
            self.get_url(task.id, comment.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_delete_comment_user_not_an_author(
        self,
        async_client,
        create_user,
        create_team,
        create_task,
        create_comment,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        author, _ = await create_user(
            UserCreate(email="author@example.com", password="Pass!234")
        )
        team = await create_team(TeamCreate(name="team"), members=[user, author])
        task = await create_task(
            TaskCreate(
                description="asfas", deadline=self._some_deadline, team_id=team.id
            ),
            author=author,
        )
        comment = await create_comment(CommentCreate(text="comment"), task, author)

        response = await async_client.delete(
            self.get_url(task.id, comment.id),
            headers=get_authorization_header(token),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
