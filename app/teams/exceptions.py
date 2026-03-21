from app.auth.models import User


class TeamDoesNotExistError(Exception):
    def __init__(self, team_id: int):
        self.team_id = team_id
        self.message = f"Team with id {team_id} does not exist"
        super().__init__(self.message)


class TeamAlreadyExistsError(Exception):
    def __init__(self, team_name: str):
        self.team_name = team_name
        self.message = f"Team with name {team_name} already exists"
        super().__init__(self.message)


class UserAlreadyInTeamError(Exception):
    """Raised when trying to add a user already assigned to a team to a new one"""

    def __init__(self, user: User):
        self.user = user
        self.message = f"User {self.user.email} already in team {self.user.team_id}"
        super().__init__(self.message)
