from fastapi import FastAPI

from app.core.config import settings
from app.lifespan import lifespan
from app.middleware.logging import LoggingMiddleware
from app.middleware.metrics import MetricsMiddleware
from app.routers import (
    auth,
    documents,
    health,
    metrics,
    query,
    root,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    LoggingMiddleware,
)

app.add_middleware(MetricsMiddleware)

app.include_router(root.router)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(metrics.router)
