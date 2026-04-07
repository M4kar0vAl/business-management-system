from fastapi_users.authentication import BearerTransport, CookieTransport

from app.config import settings

bearer_transport = BearerTransport(tokenUrl="auth/bearer/login")
cookie_transport = CookieTransport(
    cookie_name=settings.AUTHENTICATION.COOKIE.NAME,
    cookie_max_age=settings.AUTHENTICATION.COOKIE.MAX_AGE,
    cookie_path=settings.AUTHENTICATION.COOKIE.PATH,
    cookie_domain=settings.AUTHENTICATION.COOKIE.DOMAIN,
    cookie_secure=settings.AUTHENTICATION.COOKIE.SECURE,
    cookie_httponly=settings.AUTHENTICATION.COOKIE.HTTPONLY,
    cookie_samesite=settings.AUTHENTICATION.COOKIE.SAMESITE,
)
