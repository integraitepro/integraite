"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import AsyncGenerator

from app.core.config import settings

# Create base class for models
Base = declarative_base()

# SQLite setup for development (async)
if settings.DATABASE_URL.startswith("sqlite"):
    # Convert sqlite:/// to sqlite+aiosqlite:/// for async support
    async_database_url = settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
    engine = create_async_engine(
        async_database_url,
        echo=settings.DEBUG,
        future=True,
        connect_args={"check_same_thread": False}
    )
else:
    # For PostgreSQL/MySQL (when we migrate later)
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
    )

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """
    Create all database tables
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
