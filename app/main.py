from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.views import router

app: FastAPI = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

app.include_router(router)

# Development middleware
if settings.DEBUG:
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Health check endpoint
@app.get("/health")
async def health_check() -> dict:
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event() -> None:
    print(f"\n🚀 Launching {settings.APP_NAME}")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    print(f"\n💤 Shutting down {settings.APP_NAME}")
