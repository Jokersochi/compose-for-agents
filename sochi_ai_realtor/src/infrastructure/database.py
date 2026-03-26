import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Default fallback for local testing
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+asyncpg://sochi_user:sochi_password@localhost:5432/sochi_ai"
)

engine: AsyncEngine = create_async_engine(
    DATABASE_URL, echo=True, future=True, pool_size=5, max_overflow=10
)

async_session_maker = sessionmaker( # type: ignore

    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

Base = declarative_base()

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
