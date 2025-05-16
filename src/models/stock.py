from datetime import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class Stock(BaseModel):
    """주식 정보 모델"""

    __tablename__ = "stocks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    ticker = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    industry = Column(String(100), nullable=True)
    market = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # 관계 설정
    prices = relationship("Price", back_populates="stock", lazy="selectin")

    # 인덱스 설정
    __table_args__ = (
        Index("ix_stocks_ticker", "ticker", unique=True),
        Index("ix_stocks_name", "name"),
    )

    def __repr__(self):
        return f"<Stock(ticker={self.ticker}, name={self.name})>"
