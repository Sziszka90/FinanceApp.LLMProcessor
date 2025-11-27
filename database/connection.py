import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import urllib.parse
import logging
import time

# Configure logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONNECTION_STRING = os.getenv("CONNECTION_STRING")

def parse_connection_string(conn_str: str) -> str:
    """Parse SQL Server connection string to async SQLAlchemy format"""
    # Small delay to ensure environment is fully loaded
    time.sleep(20)
    
    logger.info(f"Raw connection string: {conn_str}")
    
    params = {}
    for part in conn_str.split(';'):
        if '=' in part:
            key, value = part.split('=', 1)
            params[key.strip()] = value.strip()
    
    server = params.get('Server', 'localhost')
    host, port = (server.split(',') + ['1433'])[:2]
    
    database = params.get('Database', 'FinanceAppDB')
    user = params.get('User', 'FinanceAppDB_Login')
    password = params.get('Password', 'Secret12345!')
    
    # URL encode password to handle special characters like !
    encoded_password = urllib.parse.quote_plus(password)
    
    # Log connection details (without password)
    logger.info(f"Database connection: host={host}, port={port}, database={database}, user={user}")
    
    return (
        f"mssql+aioodbc://{user}:{encoded_password}@{host}:{port}/{database}"
        "?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
    )

# Convert SQL Server connection string to async format with aioodbc
ASYNC_CONNECTION_STRING = parse_connection_string(CONNECTION_STRING)

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
