from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.auth.models import User
from app.tasks.models import Comment, Task
from app.tasks.schemas import CommentCreate, CommentUpdate


class CommentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, comment: CommentCreate, user: User, task: Task) -> Comment:
        """
        Create a new comment.

        :param comment: data to create comment with
        :param user: user who is creating the comment
        :param task: task for which the comment is created
        :return: created Comment instance
        """
        db_comment = Comment(**comment.model_dump(), user=user, task=task)
        self.session.add(db_comment)

        return db_comment

    async def get_by_id(self, comment_id: int) -> Comment | None:
        """
        Get comment by id.

        :param comment_id: id of a comment to get
        :return: Comment instance or None if it was not found
        """
        return await self.session.get(
            Comment, comment_id, options=[joinedload(Comment.user)]
        )

    async def get_comments_for_task(self, task: Task) -> list[Comment]:
        """
        Get all comments for a task.

        :param task: task to get comments for
        :return: list of comments
        """
        stmt = (
            select(Comment)
            .where(Comment.task_id == task.id)
            .options(joinedload(Comment.user))
        )
        return list(await self.session.scalars(stmt))

    @classmethod
    async def update(cls, comment: Comment, update_data: CommentUpdate) -> Comment:
        """
        Update a comment.

        :param comment: comment to update
        :param update_data: data to update the comment with
        :return: updated Comment instance
        """
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(comment, key, value)

        return comment

    async def delete(self, comment: Comment) -> None:
        """
        Delete a comment.

        :param comment: comment to delete
        :return: None
        """
        await self.session.delete(comment)
