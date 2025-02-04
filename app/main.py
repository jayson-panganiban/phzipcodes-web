from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.views import router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        default_response_class=JSONResponse,
    )

    configure_middleware(app)
    configure_routes(app)

    return app


def configure_middleware(app: FastAPI) -> None:
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

    if settings.DEBUG:
        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


def configure_routes(app: FastAPI) -> None:
    app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
    app.include_router(router)


app = create_app()


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "version": settings.VERSION}


def log_startup() -> None:
    print(f"\n🚀 Startup: {settings.APP_NAME}")


def log_shutdown() -> None:
    print(f"\n💤 Shutdown: {settings.APP_NAME}")


app.add_event_handler("startup", log_startup)
app.add_event_handler("shutdown", log_shutdown)
