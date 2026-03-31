from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, status

from app import responses
from app.auth.fastapi_users_instance import current_active_user, get_current_admin
from app.auth.schemas import UserRead
from app.auth.types import UserIdType
from app.dependencies import UOWDep
from app.tasks.schemas.tasks import TaskReadFull
from app.teams.dependencies import TeamServiceDep, current_team, team_of_current_user
from app.teams.schemas import AssignRole, TeamCreate, TeamRead

if TYPE_CHECKING:
    from app.teams.models import Team


router = APIRouter(
    prefix="/teams",
    tags=["Teams"],
    dependencies=[Depends(current_active_user)],
    responses={**responses.UNAUTHORIZED_RESPONSE},
)

ROUTE_NAME_PREFIX = "teams"
GET_TEAMS_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:get_teams"
CREATE_TEAM_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:create_team"
GET_TEAM_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:get_team"
GET_TEAM_MEMBERS_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:get_members"
GET_TEAM_TASKS_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:get_tasks"
ADD_USER_TO_TEAM_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:add_user"
REMOVE_USER_FROM_TEAM_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:remove_user"
ASSIGN_USER_ROLE_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:assign_user_role"


@router.get("/", response_model=list[TeamRead], name=GET_TEAMS_ROUTE_NAME)
async def get_teams(team_service: TeamServiceDep):
    """
    Get list of all teams.

    Active users only.
    """
    return await team_service.get_all_teams()


@router.post(
    "/",
    response_model=TeamRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
    name=CREATE_TEAM_ROUTE_NAME,
    responses={**responses.ALREADY_EXISTS_RESPONSE, **responses.FORBIDDEN_RESPONSE},
)
async def create_team(uow: UOWDep, team_service: TeamServiceDep, team: TeamCreate):
    """
    Create a new team.

    Only users with role admin or superusers can create new teams.
    """
    created_team = await team_service.create_team(team)
    await uow.flush()

    return created_team


@router.get(
    "/{team_id}",
    response_model=TeamRead,
    name=GET_TEAM_ROUTE_NAME,
    responses={**responses.NOT_FOUND_RESPONSE},
)
async def get_team_by_id(
    team: Annotated[Team, Depends(team_of_current_user(current_active_user))],
):
    """
    Get team info by id.

    In order to get the team info:
    - the team must exist
    - the current user must be a member of the team

    Active users only.
    """
    return team


@router.get(
    "/{team_id}/members",
    response_model=list[UserRead],
    responses={**responses.NOT_FOUND_RESPONSE, **responses.BAD_REQUEST_RESPONSE},
    name=GET_TEAM_MEMBERS_ROUTE_NAME,
)
async def get_team_members(
    team: Annotated[Team, Depends(team_of_current_user(current_active_user))],
    team_service: TeamServiceDep,
):
    """
    Get members of a team.

    Current user must be a member of a team.

    Active users only.
    """
    return await team_service.get_team_members(team)


@router.get(
    "/{team_id}/tasks",
    response_model=list[TaskReadFull],
    responses={**responses.NOT_FOUND_RESPONSE, **responses.BAD_REQUEST_RESPONSE},
    name=GET_TEAM_TASKS_ROUTE_NAME,
)
async def get_team_tasks(
    team: Annotated[Team, Depends(team_of_current_user(current_active_user))],
    team_service: TeamServiceDep,
):
    """
    Get tasks of a team.

    Current user must be a member of a team.

    Active users only.
    """
    return await team_service.get_team_tasks(team)


@router.post(
    "/{team_id}/members/{user_id}",
    dependencies=[Depends(get_current_admin)],
    name=ADD_USER_TO_TEAM_ROUTE_NAME,
    responses={
        **responses.SUCCESS_RESPONSE,
        **responses.FORBIDDEN_RESPONSE,
        **responses.NOT_FOUND_RESPONSE,
        **responses.BAD_REQUEST_RESPONSE,
    },
)
async def add_user_to_team(
    team: Annotated[Team, Depends(current_team)],
    user_id: UserIdType,
    team_service: TeamServiceDep,
):
    """
    Add user to team.

    In order to add user to team:
    - user with `user_id` must exist
    - team with `team_id` must exist
    - user with `user_id` must not be assigned to another team

    Only users with role admin or superusers can add users to teams.
    """
    await team_service.add_user_to_team(team, user_id)

    return {"detail": "User added successfully"}


@router.delete(
    "/members/{user_id}",
    dependencies=[Depends(get_current_admin)],
    name=REMOVE_USER_FROM_TEAM_ROUTE_NAME,
    responses={
        **responses.SUCCESS_RESPONSE,
        **responses.FORBIDDEN_RESPONSE,
        **responses.NOT_FOUND_RESPONSE,
    },
)
async def remove_user_from_team(team_service: TeamServiceDep, user_id: UserIdType):
    """
    Remove user from team.

    Only users with role admin or superusers can remove users from teams.
    """
    await team_service.remove_user_from_team(user_id)

    return {"detail": "User removed successfully"}


@router.patch(
    "/members/{user_id}",
    dependencies=[Depends(get_current_admin)],
    name=ASSIGN_USER_ROLE_ROUTE_NAME,
    response_model=UserRead,
    responses={
        **responses.FORBIDDEN_RESPONSE,
        **responses.BAD_REQUEST_RESPONSE,
        **responses.NOT_FOUND_RESPONSE,
    },
)
async def assign_user_role(
    team_service: TeamServiceDep, user_id: UserIdType, assign_role: AssignRole
):
    """
    Assign role to a user in team.

    Role 'admin' is not assignable via this endpoint!

    Only users with role admin or superusers can assign user roles.
    """
    return await team_service.assign_user_role(user_id, assign_role)
