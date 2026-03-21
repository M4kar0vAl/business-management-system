from fastapi_users import FastAPIUsers

from .backend import authentication_backend
from .dependencies import get_user_manager
from .models import User
from .types import UserIdType

fastapi_users_instance = FastAPIUsers[User, UserIdType](
    get_user_manager,
    [authentication_backend],
)
