__all__ = [
    "register_admin_views",
]

from fastapi import FastAPI
from sqladmin import Admin

from app.auth.admin import admin_authentication_backend
from app.auth.admin import register_admin_views as register_auth_admin_views
from app.database import Session
from app.tasks.admin import register_admin_views as register_task_admin_views
from app.teams.admin import register_admin_views as register_team_admin_views


def register_admin_views(app: FastAPI):
    admin = Admin(
        app, session_maker=Session, authentication_backend=admin_authentication_backend
    )

    # auth
    register_auth_admin_views(admin)

    # teams
    register_team_admin_views(admin)

    # tasks
    register_task_admin_views(admin)
