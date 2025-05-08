from sqlalchemy import Column, String
from src.models.base import Base


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    ticker = Column(String, nullable=False, unique=True, index=True)
    country = Column(
        String(2), nullable=False, index=True
    )  # 2-digit country code (e.g., US, KR, JP)

    def __repr__(self):
        return f"<Stock {self.ticker} ({self.name})>"
