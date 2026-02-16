from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import Base, engine
from app.api.public import router as public_router
from app.api.admin import router as admin_router

# import models to register metadata
import app.models  # noqa: F401


def create_app() -> FastAPI:
    app = FastAPI(
        title="N Kids Land API",
        root_path="/api",          # <= важно для nginx location /api/
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")] if settings.CORS_ORIGINS else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(public_router)
    app.include_router(admin_router)
    return app


app = create_app()

# для локалки
Base.metadata.create_all(bind=engine)
