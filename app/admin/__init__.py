__all__ = [
    "register_admin_views",
]

from fastapi import FastAPI
from sqladmin import Admin

from app.auth import admin as auth_admin
from app.database import Session


def register_admin_views(app: FastAPI):
    admin = Admin(app, session_maker=Session)

    # auth
    admin.add_view(auth_admin.AccessTokenAdmin)
    admin.add_view(auth_admin.UserAdmin)
