from app.auth.types import UserIdType
from app.tasks.models import Task


class TaskDoesNotExistError(Exception):
    """
    Raised when a task with a given id does not exist.
    """

    def __init__(self, task_id: int):
        self.task_id = task_id
        self.message = f"Task with id {self.task_id} does not exist"
        super().__init__(self.message)


class TaskAlreadyAssignedError(Exception):
    """
    Raised when trying to assign task to a user which is already assigned to another one.
    """

    def __init__(self, task: Task):
        self.task = task
        self.message = f"Task {self.task.id} is already assigned to user with id {self.task.assignee_id}"
        super().__init__(self.message)


class UserIsNotTaskAssigneeError(Exception):
    """
    Raised when a user is not assigned to the specific task, but they should be.
    """

    def __init__(self, task: Task, user_id: UserIdType):
        self.task = task
        self.user_id = user_id
        self.message = (
            f"Task {self.task} is not assigned to user with id {self.user_id}"
        )
        super().__init__(self.message)


class CommentDoesNotExistError(Exception):
    """
    Raised when a comment with a given id does not exist.
    """

    def __init__(self, comment_id: int):
        self.comment_id = comment_id
        self.message = f"Comment with id {self.comment_id} does not exist"
        super().__init__(self.message)


class CommentDoesNotBelongToUser(Exception):
    """
    Raised when user is trying to manipulate a comment which was not created by them.
    """

    def __init__(self, comment_id: int, user_id: UserIdType):
        self.comment_id = comment_id
        self.user_id = user_id
        self.message = f"Comment with id {self.comment_id} does not belong to user with id {self.user_id}"
        super().__init__(self.message)


class EvaluationDoesNotExistError(Exception):
    """
    Raised when an evaluation with a given id does not exist.
    """

    def __init__(self, evaluation_id: int):
        self.evaluation_id = evaluation_id
        self.message = f"Evaluation with id {self.evaluation_id} does not exist"
        super().__init__(self.message)
