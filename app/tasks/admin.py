from sqladmin import Admin, ModelView

from app.tasks.models import Comment, Task


class TaskAdmin(ModelView, model=Task):
    column_list = (
        Task.id,
        Task.description,
        Task.status,
        Task.created_at,
        Task.deadline,
    )
    form_excluded_columns = (Task.comments,)
    column_default_sort = (Task.created_at, True)


class CommentAdmin(ModelView, model=Comment):
    column_list = (Comment.id, Comment.user, Comment.task, Comment.created_at)
    column_default_sort = (Comment.created_at, True)


def register_admin_views(admin: Admin):
    admin.add_view(TaskAdmin)
    admin.add_view(CommentAdmin)
