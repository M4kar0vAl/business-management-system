from sqladmin import Admin, ModelView

from app.teams.models import Team


class TeamAdmin(ModelView, model=Team):
    column_list = (Team.id, Team.name, Team.description)
    column_default_sort = [  # noqa: RUF012
        (Team.id, True),
    ]


def register_admin_views(admin: Admin):
    admin.add_view(TeamAdmin)
