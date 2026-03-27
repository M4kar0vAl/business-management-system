from fastapi import status
from fastapi_users.exceptions import UserNotExists

exception_status_mapping = {
    UserNotExists: status.HTTP_404_NOT_FOUND,
}
