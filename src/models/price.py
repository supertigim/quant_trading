from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.models.base import BaseModel


class Price(BaseModel):
    """주식 가격 데이터 모델"""

    __tablename__ = "price"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(
        UUID(as_uuid=True), ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False
    )
    date = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # 관계 설정
    stock = relationship("Stock", back_populates="prices", lazy="joined")

    # 인덱스 설정
    __table_args__ = (Index("ix_price_stock_date", "stock_id", "date", unique=True),)

    def __repr__(self):
        return (
            f"<Price(stock_id={self.stock_id}, date={self.date}, close={self.close})>"
        )
