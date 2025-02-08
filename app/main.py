from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.views import router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        default_response_class=HTMLResponse,
    )

    configure_middleware(app)
    configure_routes(app)

    return app


def configure_middleware(app: FastAPI) -> None:
    """Configure middleware stack for the application."""
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next) -> HTMLResponse:
        response = await call_next(request)
        response.headers.update(settings.SECURITY_HEADERS)
        return response


def configure_routes(app: FastAPI) -> None:
    """Configure application routes and static files."""
    app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
    app.include_router(router)


app = create_app()
