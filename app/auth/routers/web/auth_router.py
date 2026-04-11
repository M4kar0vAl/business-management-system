from contextlib import suppress
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import exceptions, models
from fastapi_users.authentication import Strategy
from fastapi_users.authentication.strategy import StrategyDestroyNotSupportedError

from app.auth.backend import auth_cookie_db_backend
from app.auth.dependencies import get_user_manager
from app.auth.fastapi_users_instance import (
    current_active_user,
    fastapi_users_instance,
    unauthenticated_user_or_redirect_home,
)
from app.auth.schemas import UserCreate
from app.auth.user_manager import UserManager
from app.templates import templates

router = APIRouter(prefix="/auth")

HOME_ROUTE_NAME = "home"
LOGIN_ROUTE_NAME = "login"
LOGIN_PAGE_ROUTE_NAME = "login_page"
LOGOUT_ROUTE_NAME = "logout"
REGISTER_ROUTE_NAME = "register"
REGISTER_PAGE_ROUTE_NAME = "register_page"


@router.get(
    "/login",
    dependencies=[Depends(unauthenticated_user_or_redirect_home)],
    response_class=HTMLResponse,
    name=LOGIN_PAGE_ROUTE_NAME,
)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={"title": "Login"},
    )


@router.post(
    "/login",
    dependencies=[Depends(unauthenticated_user_or_redirect_home)],
    response_class=HTMLResponse,
    name=LOGIN_ROUTE_NAME,
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    strategy: Annotated[
        Strategy[models.UP, models.ID], Depends(auth_cookie_db_backend.get_strategy)
    ],
):
    user = await user_manager.authenticate(form_data)

    if user is None or not user.is_active:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "title": "Login",
                "form_data": form_data,
                "error": "Incorrect username or password",
            },
        )

    token = await strategy.write_token(user)
    response = RedirectResponse(
        request.url_for(HOME_ROUTE_NAME), status_code=status.HTTP_303_SEE_OTHER
    )
    auth_cookie_db_backend.transport._set_login_cookie(response, token)

    await user_manager.on_after_login(user, request, response)

    return response


@router.post(
    "/logout",
    dependencies=[Depends(current_active_user)],
    response_class=RedirectResponse,
    name=LOGOUT_ROUTE_NAME,
)
async def logout(
    request: Request,
    user_token: Annotated[
        tuple[models.UP, str],
        Depends(
            fastapi_users_instance.authenticator.current_user_token(
                active=True, verified=False
            )
        ),
    ],
    strategy: Annotated[
        Strategy[models.UP, models.ID], Depends(auth_cookie_db_backend.get_strategy)
    ],
):
    user, token = user_token
    with suppress(StrategyDestroyNotSupportedError):
        await strategy.destroy_token(token, user)

    response = RedirectResponse(
        request.url_for(HOME_ROUTE_NAME), status_code=status.HTTP_303_SEE_OTHER
    )

    return auth_cookie_db_backend.transport._set_logout_cookie(response)


@router.get(
    "/register",
    dependencies=[Depends(unauthenticated_user_or_redirect_home)],
    response_class=HTMLResponse,
    name=REGISTER_PAGE_ROUTE_NAME,
)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="auth/register.html", context={"title": "Register"}
    )


@router.post(
    "/register",
    dependencies=[Depends(unauthenticated_user_or_redirect_home)],
    response_class=HTMLResponse,
    name=REGISTER_ROUTE_NAME,
)
async def register(
    user_data: Annotated[UserCreate, Form()],
    request: Request,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
):
    error = None
    try:
        await user_manager.create(user_data, safe=True, request=request)
    except exceptions.UserAlreadyExists:
        error = "User with this email already exists"
    except exceptions.InvalidPasswordException as e:
        error = e.reason

    if error is not None:
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={"title": "Register", "form_data": user_data, "error": error},
        )

    return RedirectResponse(
        request.url_for(LOGIN_PAGE_ROUTE_NAME),
        status_code=status.HTTP_303_SEE_OTHER,
    )
