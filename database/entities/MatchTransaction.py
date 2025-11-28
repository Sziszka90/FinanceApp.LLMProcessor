from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import uuid

Base = declarative_base()

class MatchTransaction(Base):
    __tablename__ = "MatchTransaction"
    
    Id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    Transaction = Column(String, nullable=False)
    TransactionGroup = Column(String, nullable=False)
    CorrelationId = Column(String, nullable=False)
    Created = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    Modified = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
