from app.auth.models import User
from app.auth.types import UserIdType
from app.tasks.models import Task, TaskStatus


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


class InvalidTaskStatusError(Exception):
    """
    Raised when a task has an invalid status for the operation to perform.
    """

    def __init__(self, task: Task, expected_status: TaskStatus):
        self.task = task
        self.expected_status = expected_status
        self.message = (
            f"Invalid task status: {self.task.status}. Expected: {self.expected_status}"
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


class EvaluationDoesNotExistError(Exception):
    """
    Raised when an evaluation with a given id does not exist.
    """

    def __init__(self, evaluation_id: int):
        self.evaluation_id = evaluation_id
        self.message = f"Evaluation with id {self.evaluation_id} does not exist"
        super().__init__(self.message)


class EvaluationAlreadyExistsError(Exception):
    """
    Raised when user evaluation of the given task already exists.
    """

    def __init__(self, user: User, task: Task):
        self.user = user
        self.task = task
        self.message = (
            f"User {self.user.email} evaluation of task {self.task.id} already exists"
        )
        super().__init__(self.message)


class EvaluationDoesNotBelongToTaskError(Exception):
    """
    Raised when evaluation should belong to the specific task, but it is not.
    """

    def __init__(self, evaluation_id: int, task_id: int):
        self.evaluation_id = evaluation_id
        self.task_id = task_id
        self.message = f"Evaluation with id {self.evaluation_id} does not belong to task with id {self.task_id}"
        super().__init__(self.message)
