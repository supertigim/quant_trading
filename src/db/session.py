from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from src.core.config import settings

# Async engine 생성
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=settings.DB_ECHO,
    future=True,
)

# Async session factory 생성
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db():
    """데이터베이스 세션을 제공하는 의존성 함수"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
