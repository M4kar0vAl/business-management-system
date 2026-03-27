from fastapi import APIRouter, Depends, status

from app.auth.fastapi_users_instance import current_active_user, get_current_admin
from app.auth.types import UserIdType
from app.dependencies import UOWDep
from app.teams.dependencies import TeamServiceDep
from app.teams.schemas import AssignRole, TeamCreate, TeamRead, TeamReadFull

router = APIRouter(
    prefix="/teams", tags=["Teams"], dependencies=[Depends(current_active_user)]
)

ROUTE_NAME_PREFIX = "teams"
GET_TEAMS_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:get_teams"
CREATE_TEAM_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:create_team"
GET_TEAM_ROUTE_NAME = f"{ROUTE_NAME_PREFIX}:get_team"
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
)
async def create_team(uow: UOWDep, team_service: TeamServiceDep, team: TeamCreate):
    """
    Create a new team.

    Only users with role admin or superusers can create new teams.
    """
    created_team = await team_service.create_team(team)
    await uow.flush()

    return created_team


@router.get("/{team_id}", response_model=TeamReadFull, name=GET_TEAM_ROUTE_NAME)
async def get_team_by_id(team_service: TeamServiceDep, team_id: int):
    """
    Get team info by id.

    Active users only.
    """
    return await team_service.get_team_by_id(team_id)


@router.post(
    "/{team_id}/members/{user_id}",
    dependencies=[Depends(get_current_admin)],
    name=ADD_USER_TO_TEAM_ROUTE_NAME,
)
async def add_user_to_team(
    team_service: TeamServiceDep, team_id: int, user_id: UserIdType
):
    """
    Add user to team.

    Only users with role admin or superusers can add users to teams.
    """
    await team_service.add_user_to_team(team_id, user_id)

    return {"detail": "User added successfully"}


@router.delete(
    "/members/{user_id}",
    dependencies=[Depends(get_current_admin)],
    name=REMOVE_USER_FROM_TEAM_ROUTE_NAME,
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
