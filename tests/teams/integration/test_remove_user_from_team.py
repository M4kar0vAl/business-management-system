from datetime import UTC, datetime, timedelta

from fastapi import status

from app.auth.models import Role
from app.auth.schemas import UserCreate
from app.auth.types import UserIdType
from app.tasks.schemas import TaskCreate
from app.teams.routers import REMOVE_USER_FROM_TEAM_ROUTE_NAME
from app.teams.schemas import TeamCreate
from tests.mixins import GetUrlMixin


class TestRemoveUserFromTeam(GetUrlMixin):
    url_name = REMOVE_USER_FROM_TEAM_ROUTE_NAME

    def get_url(self, user_id: UserIdType):
        return super().get_url(user_id=user_id)

    async def test_remove_user_from_team(
        self, async_client, create_user, create_team, get_authorization_header, user_db
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN),
            authenticate=True,
        )
        await create_team(TeamCreate(name="team"), members=[user])

        response = await async_client.delete(
            self.get_url(user.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_200_OK

        updated_user = await user_db.get(user.id)
        assert updated_user is not None
        assert updated_user.team_id is None

    async def test_remove_user_from_team_unauthenticated(
        self, async_client, create_user, create_team
    ):
        user, _ = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN)
        )
        await create_team(TeamCreate(name="team"), members=[user])

        response = await async_client.delete(self.get_url(user.id))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_remove_user_from_team_inactive(
        self, async_client, create_user, create_team, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(
                email="user@example.com",
                password="Pass!234",
                role=Role.ADMIN,
                is_active=False,
            ),
            authenticate=True,
        )
        await create_team(TeamCreate(name="team"), members=[user])

        response = await async_client.delete(
            self.get_url(user.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_remove_user_from_team_not_an_admin(
        self, async_client, create_user, create_team, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234"), authenticate=True
        )
        await create_team(TeamCreate(name="team"), members=[user])

        response = await async_client.delete(
            self.get_url(user.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_remove_user_from_team_not_in_team_ignored(
        self, async_client, create_user, get_authorization_header
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN),
            authenticate=True,
        )

        response = await async_client.delete(
            self.get_url(user.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_200_OK

    async def test_remove_user_from_team_user_does_not_exist(
        self, async_client, create_user, get_authorization_header
    ):
        _, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN),
            authenticate=True,
        )

        response = await async_client.delete(
            self.get_url(0), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_remove_user_from_team_unassigns_from_team_tasks(
        self,
        async_client,
        create_user,
        create_team,
        create_task,
        user_db,
        task_repository,
        get_authorization_header,
    ):
        user, token = await create_user(
            UserCreate(email="user@example.com", password="Pass!234", role=Role.ADMIN),
            authenticate=True,
        )
        team = await create_team(TeamCreate(name="team"), members=[user])
        task_assigned = await create_task(
            TaskCreate(
                description="asfas",
                deadline=datetime.now(UTC) + timedelta(days=1),
                team_id=team.id,
            ),
            author=user,
            assignee=user,
        )

        response = await async_client.delete(
            self.get_url(user.id), headers=get_authorization_header(token)
        )

        assert response.status_code == status.HTTP_200_OK

        updated_user = await user_db.get(user.id)
        updated_task = await task_repository.get_by_id(task_assigned.id)
        assert updated_user is not None
        assert updated_user.team_id is None
        assert updated_task.assignee_id is None
