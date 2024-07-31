from starlette.middleware.sessions import SessionMiddleware

from app.middleware.logging import LoggingMiddleware
from app.middleware.security_header import SecurityHeadersMiddleware
from app.middleware.rate_limiter import setup_rate_limiter

from app.config import SESSION_MIDDL_SECRET_KEY


def setup_middlewares(app):
    app.add_middleware(SessionMiddleware, secret_key=SESSION_MIDDL_SECRET_KEY)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    setup_rate_limiter(app)
