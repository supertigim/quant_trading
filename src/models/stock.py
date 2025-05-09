from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from src.models.base import BaseModel
import uuid


class Stock(BaseModel):
    __tablename__ = "stocks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    ticker = Column(String, unique=True, index=True, nullable=False)
    country = Column(String, nullable=False)
    market = Column(String, nullable=True)
    last_updated = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<Stock(id='{self.id}', name='{self.name}', ticker='{self.ticker}')>"
