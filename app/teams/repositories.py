from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.models import Role, User
from app.tasks.models import Task
from app.teams.models import Team
from app.teams.schemas import TeamCreate, TeamUpdate


class TeamRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, team: TeamCreate) -> Team:
        """
        Creates a new team in the database

        :param team: team to create
        :return: created team
        """
        db_team = Team(**team.model_dump())
        self.session.add(db_team)

        return db_team

    async def get_by_id(self, id_: int) -> Team | None:
        """
        Get team by id

        :param id_: id of a team
        :return: Team instance or None
        """
        return await self.session.get(Team, id_)

    async def get_by_id_full(self, id_: int) -> Team | None:
        """
        Get team by id with all relations.

        :param id_: id of a team
        :return: Team instance or None
        """
        stmt = (
            select(Team)
            .where(Team.id == id_)
            .options(selectinload(Team.users), selectinload(Team.tasks))
        )
        return (await self.session.scalars(stmt)).one_or_none()

    async def get_by_name(self, name: str) -> Team | None:
        """
        Get team by name

        :param name: name of a team
        :return: Team instance or None if not found
        """
        stmt = select(Team).where(Team.name == name)

        return (await self.session.scalars(stmt)).one_or_none()

    async def get_all(self) -> list[Team]:
        """
        Returns all teams in the database

        :return: list of all teams
        """
        return list(await self.session.scalars(select(Team)))

    @classmethod
    async def update(cls, team: Team, update_data: TeamUpdate) -> Team:
        """
        Updates a team in the database

        :param team: team to update
        :param update_data: data to update with
        :return: updated team
        """
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(team, key, value)

        return team

    async def delete(self, team: Team) -> None:
        """
        Deletes a team from the database

        :param team: team to delete
        :return: None
        """
        await self.session.delete(team)

    @classmethod
    async def assign_user_to_team(cls, team: Team, user: User) -> None:
        """
        Adds a user to the team

        :param team: team to add a user to
        :param user: user to add in team
        :return: None
        """
        user.team = team

    @classmethod
    async def remove_user_from_team(cls, user: User) -> None:
        """
        Removes a user from their current team. Does nothing if the user is not assigned to one

        :param user: user to remove from a team
        :return: None
        """
        user.team = None

    async def get_team_members(self, team: Team) -> list[User]:
        """
        Returns all users in the team

        :param team: team to get members of
        :return: list of users in the team
        """
        stmt = select(User).where(User.team_id == team.id)

        return list(await self.session.scalars(stmt))

    async def get_team_tasks(self, team: Team) -> list[Task]:
        """
        Returns all tasks associated with the team

        :param team: team to get tasks of
        :return: list of tasks associated with the team
        """
        stmt = select(Task).where(Task.team_id == team.id)

        return list(await self.session.scalars(stmt))

    @classmethod
    async def assign_user_role(cls, user: User, role: Role) -> None:
        """
        Assign a role to the user in a team

        :param user: user to assign role to
        :param role: role to assign
        :return: None
        """
        user.role = role
