from fastapi import APIRouter, Depends, status

from app.auth.fastapi_users_instance import current_active_user, get_current_admin
from app.auth.types import UserIdType
from app.dependencies import UOWDep
from app.teams.dependencies import TeamServiceDep
from app.teams.schemas import TeamCreate, TeamRead, TeamReadFull

router = APIRouter(
    prefix="/teams", tags=["Teams"], dependencies=[Depends(current_active_user)]
)


@router.get("/", response_model=list[TeamRead])
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
)
async def create_team(uow: UOWDep, team_service: TeamServiceDep, team: TeamCreate):
    """
    Create a new team.

    Only users with role admin or superusers can create new teams.
    """
    created_team = await team_service.create_team(team)
    await uow.flush()

    return created_team


@router.get("/{team_id}", response_model=TeamReadFull)
async def get_team_by_id(team_service: TeamServiceDep, team_id: int):
    """
    Get team info by id.

    Active users only.
    """
    return await team_service.get_team_by_id(team_id)


@router.post("/{team_id}/members/{user_id}", dependencies=[Depends(get_current_admin)])
async def add_user_to_team(
    team_service: TeamServiceDep, team_id: int, user_id: UserIdType
):
    """
    Add user to team.

    Only users with role admin or superusers can add users to teams.
    """
    await team_service.add_user_to_team(team_id, user_id)

    return {"detail": "User added successfully"}


@router.delete("/members/{user_id}", dependencies=[Depends(get_current_admin)])
async def remove_user_from_team(team_service: TeamServiceDep, user_id: UserIdType):
    """
    Remove user from team.

    Only users with role admin or superusers can remove users from teams.
    """
    await team_service.remove_user_from_team(user_id)

    return {"detail": "User removed successfully"}
