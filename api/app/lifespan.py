from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.base import Base
from app.db.database import engine
from app.models import *
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("🚀 Starting Enterprise RAG Platform")

    if settings.APP_ENV == "development":
        Base.metadata.create_all(bind=engine)

    yield

    print("🛑 Shutting down Enterprise RAG Platform")