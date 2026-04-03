from typing import TYPE_CHECKING

from app.tasks.exceptions import CommentDoesNotExistError
from app.tasks.repositories import CommentRepository
from app.tasks.schemas import CommentCreate, CommentUpdate
from app.uow import UnitOfWork

if TYPE_CHECKING:
    from app.auth.models import User
    from app.tasks.models import Comment, Task


class CommentService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.comment_repo = CommentRepository(uow.session)

    async def create_comment(
        self, comment: CommentCreate, user: User, task: Task
    ) -> Comment:
        """
        Create a new comment.

        :param comment: data to create comment with
        :param user: user who is creating the comment
        :param task: task to comment
        :return: created Comment instance
        """
        return await self.comment_repo.create(comment, user, task)

    async def get_comment_by_id(self, comment_id: int) -> Comment:
        """
        Get comment by id.

        :param comment_id: id of a comment to get
        :return: Comment instance
        :raises CommentDoesNotExistError: if the comment with the given id does not exist
        """
        comment = await self.comment_repo.get_by_id(comment_id)

        if not comment:
            raise CommentDoesNotExistError(comment_id)

        return comment

    async def get_comments_for_task(self, task: Task) -> list[Comment]:
        """
        Get all comments for a task.

        :param task: task to get comments for
        :return: list of comments
        """
        return await self.comment_repo.get_comments_for_task(task)

    async def update_comment(
        self,
        comment: Comment,
        update_data: CommentUpdate,
    ) -> Comment:
        """
        Update a comment.

        :param comment: comment to update
        :param update_data: data to update the comment with
        :return: updated Comment instance
        """
        return await self.comment_repo.update(comment, update_data)

    async def delete_comment(self, comment: Comment) -> None:
        """
        Delete a comment.

        :param comment: comment to delete
        :return: None
        """
        await self.comment_repo.delete(comment)
