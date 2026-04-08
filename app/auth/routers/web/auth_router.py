from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.backend import auth_cookie_db_backend
from app.auth.fastapi_users_instance import (
    current_active_user,
    unauthenticated_user_or_redirect_home,
)
from app.auth.schemas import UserCreate
from app.dependencies import AsyncClientDep
from app.templates import templates

router = APIRouter(prefix="/auth")

HOME_ROUTE_NAME = "home"
API_LOGIN_ROUTE_NAME = f"auth:{auth_cookie_db_backend.name}.login"
LOGIN_ROUTE_NAME = "login"
LOGIN_PAGE_ROUTE_NAME = "login_page"
API_LOGOUT_ROUTE_NAME = f"auth:{auth_cookie_db_backend.name}.logout"
LOGOUT_ROUTE_NAME = "logout"
API_REGISTER_ROUTE_NAME = "register:register"
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
    client: AsyncClientDep,
    request: Request,
):
    res = await client.post(
        str(request.url_for(API_LOGIN_ROUTE_NAME)),
        data={"username": form_data.username, "password": form_data.password},
    )

    if res.status_code == status.HTTP_204_NO_CONTENT:
        response = RedirectResponse(
            request.url_for(HOME_ROUTE_NAME), status_code=status.HTTP_303_SEE_OTHER
        )
        for name, value in res.cookies.items():
            response.set_cookie(key=name, value=value, httponly=True)
        return response

    error = res.json().get("detail")

    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={
            "title": "Login",
            "form_data": form_data,
            "error": error,
        },
    )


@router.post(
    "/logout",
    dependencies=[Depends(current_active_user)],
    response_class=RedirectResponse,
    name=LOGOUT_ROUTE_NAME,
)
async def logout(client: AsyncClientDep, request: Request):
    await client.post(
        str(request.url_for(API_LOGOUT_ROUTE_NAME)), cookies=request.cookies
    )
    return RedirectResponse(
        request.url_for(HOME_ROUTE_NAME), status_code=status.HTTP_303_SEE_OTHER
    )


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
    user_data: Annotated[UserCreate, Form()], client: AsyncClientDep, request: Request
):
    res = await client.post(
        str(request.url_for(API_REGISTER_ROUTE_NAME)),
        json=user_data.model_dump(),
    )

    if res.status_code == status.HTTP_201_CREATED:
        return RedirectResponse(
            request.url_for(LOGIN_PAGE_ROUTE_NAME),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    error = res.json().get("detail")

    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={"title": "Register", "form_data": user_data, "error": error},
    )
