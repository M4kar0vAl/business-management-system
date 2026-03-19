import secrets
from typing import Any

from fastapi_users.password import PasswordHelper
from sqladmin import ModelView
from starlette.requests import Request

from app.admin.converter import ModelConverter
from app.auth.models import AccessToken, User

password_helper = PasswordHelper()


class AccessTokenAdmin(ModelView, model=AccessToken):
    column_list = (AccessToken.token, AccessToken.user_id, AccessToken.created_at)
    form_converter = ModelConverter
    form_include_pk = True
    can_edit = False
    form_create_rules = ("user",)
    column_default_sort = [  # noqa: RUF012
        (AccessToken.created_at, True),
    ]

    def insert_model(self, request: Request, data: dict) -> Any:
        data.update(token=secrets.token_urlsafe())

        return super().insert_model(request=request, data=data)


class UserAdmin(ModelView, model=User):
    column_list = (
        User.id,
        User.email,
        User.is_manager,
        User.is_superuser,
        User.is_active,
    )

    column_labels = {  # noqa: RUF012
        User.hashed_password: "Password",
    }

    form_excluded_columns = (User.access_tokens,)

    async def on_model_change(
        self,
        data: dict,
        model: Any,
        is_created: bool,
        request: Request,  # noqa: ARG002
    ) -> None:
        # data contains raw password
        raw_password = data.get("hashed_password") or password_helper.generate()

        if is_created or model.hashed_password != raw_password:
            data.update(hashed_password=password_helper.hash(raw_password))
