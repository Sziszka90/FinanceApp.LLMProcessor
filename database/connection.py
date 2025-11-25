import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

CONNECTION_STRING = os.getenv(
    "CONNECTION_STRING",
    "Server=localhost,1433;Database=FinanceAppDB;User=FinanceAppDB_Login;Password=Secret12345!;Encrypt=False;"
)

# Convert SQL Server connection string to async format with aioodbc
# mssql+aioodbc://user:password@host:port/database?driver=ODBC+Driver+18+for+SQL+Server
ASYNC_CONNECTION_STRING = (
    "mssql+aioodbc://FinanceAppDB_Login:Secret12345!@localhost:1433/FinanceAppDB"
    "?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
)

engine = create_async_engine(
    ASYNC_CONNECTION_STRING,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    echo=False
)

SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async dependency function for FastAPI to get database session.
    """
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
