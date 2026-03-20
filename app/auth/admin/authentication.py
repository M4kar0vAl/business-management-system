from typing import TYPE_CHECKING

from fastapi.security import OAuth2PasswordRequestForm
from sqladmin.authentication import AuthenticationBackend

from app.auth.backend import authentication_backend
from app.auth.models import AccessToken, User
from app.auth.user_manager import UserManager
from app.config import settings
from app.database import Session

if TYPE_CHECKING:
    from fastapi import Request
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class AdminAuth(AuthenticationBackend):
    def __init__(
        self,
        session_maker: async_sessionmaker[AsyncSession],
        secret_key: str,
    ):
        super().__init__(secret_key=secret_key)
        self.session_maker = session_maker

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        async with self.session_maker() as session:
            user = await self._authenticate_user(session, username, password)

            if not self.is_user_allowed(user):
                return False

            token = await self._write_token(session, user)

        request.session.update({"token": token})

        return True

    async def logout(self, request: Request) -> bool:
        token = request.session.get("token")

        if token:
            async with self.session_maker() as session:
                user = await self._read_token(session, token)

                if user:
                    await self._destroy_token(session, token, user)

        request.session.clear()

        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        async with self.session_maker() as session:
            user = await self._read_token(session, token)

            if not self.is_user_allowed(user):
                request.session.pop("token", None)
                return False

        return True

    @classmethod
    async def _authenticate_user(
        cls, session: AsyncSession, username: str, password: str
    ) -> User:
        user_manager = cls._get_user_manager(session)
        return await user_manager.authenticate(
            OAuth2PasswordRequestForm(username=username, password=password)
        )

    @classmethod
    def is_user_allowed(cls, user: User | None) -> bool:
        # only superusers have access to admin panel
        return user and user.is_active and user.is_superuser

    @classmethod
    def _get_user_manager(cls, session: AsyncSession) -> UserManager:
        user_db = User.get_db(session)
        return UserManager(user_db)

    @classmethod
    def _get_strategy(cls, session: AsyncSession):
        access_token_db = AccessToken.get_db(session)
        return authentication_backend.get_strategy(access_token_db)

    async def _read_token(self, session: AsyncSession, token: str) -> User | None:
        user_manager = self._get_user_manager(session)
        strategy = self._get_strategy(session)
        return await strategy.read_token(token, user_manager)

    async def _write_token(self, session: AsyncSession, user: User) -> str:
        strategy = self._get_strategy(session)
        return await strategy.write_token(user)

    async def _destroy_token(
        self, session: AsyncSession, token: str, user: User
    ) -> None:
        strategy = self._get_strategy(session)
        await strategy.destroy_token(token, user)


admin_authentication_backend = AdminAuth(
    Session, secret_key=settings.AUTHENTICATION.ADMIN_PANEL_SECRET_KEY.get_secret_value()
)
