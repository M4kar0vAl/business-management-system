__all__ = [
    "register_admin_views",
]

from fastapi import FastAPI
from sqladmin import Admin

from app.auth.admin import views as auth_admin
from app.auth.admin.authentication import admin_authentication_backend
from app.database import Session


def register_admin_views(app: FastAPI):
    admin = Admin(
        app, session_maker=Session, authentication_backend=admin_authentication_backend
    )

    # auth
    admin.add_view(auth_admin.AccessTokenAdmin)
    admin.add_view(auth_admin.UserAdmin)
