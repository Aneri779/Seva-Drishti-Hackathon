"""
Database session — PostgreSQL + asyncpg only.
No SQLite, no in-memory fallback.
If the DB is unreachable, the application FAILS loudly at startup.
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Fail immediately if DATABASE_URL not set (validated by pydantic settings)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.is_dev,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    connect_args={
        "server_settings": {"application_name": "sardrishti_api"},
        "command_timeout": 30,
    }
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass
