"""Database Session and Engine Management."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from backend.app.core.config import settings
from backend.app.database.base import Base

# Ensure SQLite URL starts with sqlite+aiosqlite://
database_url = settings.DATABASE_URL
if database_url.startswith("sqlite:///"):
    database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

_is_sqlite = "sqlite" in database_url

# For SQLite: timeout=30 (wait up to 30s for lock), check_same_thread=False
_connect_args = (
    {"check_same_thread": False, "timeout": 30} if _is_sqlite else {}
)

engine = create_async_engine(
    database_url,
    echo=False,
    connect_args=_connect_args,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables and configure SQLite for concurrent access."""
    from backend.app.models import research  # noqa: F401

    async with engine.begin() as conn:
        # Enable WAL journal mode so readers don't block the writer
        if _is_sqlite:
            from sqlalchemy import text
            await conn.execute(text("PRAGMA journal_mode=WAL"))
            await conn.execute(text("PRAGMA busy_timeout=30000"))
        await conn.run_sync(Base.metadata.create_all)
