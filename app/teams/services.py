from app.auth.models import User
from app.auth.types import UserIdType
from app.auth.user_manager import UserManager
from app.tasks.models import Task
from app.teams.exceptions import (
    TeamAlreadyExistsError,
    TeamDoesNotExistError,
    UserAlreadyInTeamError,
    UserNotInTeamError,
)
from app.teams.models import Team
from app.teams.repositories import TeamRepository
from app.teams.schemas import AssignRole, TeamCreate
from app.uow import UnitOfWork


class TeamService:
    def __init__(self, uow: UnitOfWork, user_manager: UserManager):
        self.uow = uow
        self.team_repo = TeamRepository(self.uow.session)
        self.user_manager = user_manager

    async def create_team(self, team_data: TeamCreate) -> Team:
        """
        Creates a new team

        :param team_data: team data
        :return: Team instance
        :raises: TeamAlreadyExistsError if a team with the given name already exists
        """
        if await self.team_repo.get_by_name(team_data.name) is not None:
            raise TeamAlreadyExistsError(team_data.name)

        return await self.team_repo.create(team_data)

    async def get_team_by_id(self, team_id: int) -> Team:
        """
        Get team by id.

        :param team_id: id of a team to get
        :param full: boolean indicating whether to return team with all its relations
        :return: Team instance
        :raises: TeamDoesNotExistError: if a team with the given id does not exist
        """
        team = await self.team_repo.get_by_id(team_id)

        if not team:
            raise TeamDoesNotExistError(team_id)

        return team

    async def get_all_teams(self) -> list[Team]:
        """
        Get all teams

        :return: list of teams
        """
        return await self.team_repo.get_all()

    async def get_team_members(self, team: Team) -> list[User]:
        """
        Get all users who are members of the team

        :param team: the team to get members of
        :return: list of users
        """
        return await self.team_repo.get_team_members(team)

    async def get_team_tasks(self, team: Team) -> list[Task]:
        """
        Get all tasks associated with the team.

        :param team: the team to get tasks for
        :return: list of tasks
        """
        return await self.team_repo.get_team_tasks(team)

    async def add_user_to_team(self, team: Team, user_id: UserIdType) -> None:
        """
        Add a user to the team

        :param team: the team to add a user to
        :param user_id: id of a user to add to a team
        :return: None
        :raises: UserAlreadyInTeamError if a user is already assigned to a team
        """
        user = await self.user_manager.get(user_id)

        if user.team:
            raise UserAlreadyInTeamError(user)

        await self.team_repo.assign_user_to_team(team, user)

    async def remove_user_from_team(self, user_id: UserIdType) -> None:
        """
        Remove a user from the team

        :param user_id: id of a user to remove from their current team
        :return: None
        """
        user = await self.user_manager.get(user_id)

        await self.team_repo.remove_user_from_team(user)

    async def assign_user_role(
        self, user_id: UserIdType, assign_role: AssignRole
    ) -> User:
        """
        Assign a role to a user in team

        :param user_id: id of a user to assign role to
        :param assign_role: role to assign
        :return: User with updated role
        """
        user = await self.user_manager.get(user_id)

        if not user.team_id:
            raise UserNotInTeamError(user)

        await self.team_repo.assign_user_role(user, assign_role.role)

        return user
