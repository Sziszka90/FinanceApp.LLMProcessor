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
    
    # Strip quotes from the entire connection string first
    conn_str = conn_str.strip().strip('"').strip("'")
    
    params = {}
    for part in conn_str.split(';'):
        if '=' in part:
            key, value = part.split('=', 1)
            # Strip whitespace and quotes
            params[key.strip()] = value.strip().strip('"').strip("'")
    
    server = params.get('Server')
    logger.info(f"Server value from params: {server}")
    
    # Remove 'tcp:' prefix if present
    if server and server.startswith('tcp:'):
        server = server[4:]
    
    # Handle both comma and colon as separators
    if ',' in server:
        parts = server.split(',')
        host = parts[0].strip()
        port = parts[1].strip() if len(parts) > 1 else '1433'
    elif ':' in server:
        parts = server.split(':')
        host = parts[0].strip()
        port = parts[1].strip() if len(parts) > 1 else '1433'
    else:
        host = server
        port = '1433'
    
    # Support both 'Database' and 'Initial Catalog'
    database = params.get('Database') or params.get('Initial Catalog')
    # Support both 'User' and 'User ID'
    user = params.get('User') or params.get('User ID')
    password = params.get('Password')
    
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
