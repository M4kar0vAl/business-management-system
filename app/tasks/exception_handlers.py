from fastapi import status

from app.tasks.exceptions import (
    CommentDoesNotExistError,
    EvaluationAlreadyExistsError,
    EvaluationDoesNotBelongToTaskError,
    EvaluationDoesNotExistError,
    InvalidTaskStatusError,
    TaskAlreadyAssignedError,
    TaskDoesNotExistError,
    UserIsNotTaskAssigneeError,
)

exception_status_mapping = {
    TaskDoesNotExistError: status.HTTP_404_NOT_FOUND,
    TaskAlreadyAssignedError: status.HTTP_400_BAD_REQUEST,
    UserIsNotTaskAssigneeError: status.HTTP_400_BAD_REQUEST,
    InvalidTaskStatusError: status.HTTP_400_BAD_REQUEST,
    CommentDoesNotExistError: status.HTTP_404_NOT_FOUND,
    EvaluationDoesNotExistError: status.HTTP_404_NOT_FOUND,
    EvaluationAlreadyExistsError: status.HTTP_400_BAD_REQUEST,
    EvaluationDoesNotBelongToTaskError: status.HTTP_400_BAD_REQUEST,
}
