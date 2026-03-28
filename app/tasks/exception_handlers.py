from fastapi import status

from app.tasks.exceptions import (
    CommentDoesNotBelongToUser,
    CommentDoesNotExistError,
    TaskAlreadyAssignedError,
    TaskDoesNotExistError,
)

exception_status_mapping = {
    TaskDoesNotExistError: status.HTTP_404_NOT_FOUND,
    TaskAlreadyAssignedError: status.HTTP_400_BAD_REQUEST,
    CommentDoesNotExistError: status.HTTP_404_NOT_FOUND,
    CommentDoesNotBelongToUser: status.HTTP_400_BAD_REQUEST,
}
