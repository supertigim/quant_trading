from typing import Optional

from pydantic import BaseModel, Field


class StockBase(BaseModel):
    name: str = Field(..., description="Stock name")
    ticker: str = Field(..., description="Stock ticker symbol")
    country: str = Field(
        ...,
        min_length=2,
        max_length=2,
        description="2-digit country code (e.g., US, KR, JP)",
    )
    market: Optional[str] = Field(
        None, description="Market type (e.g., KOSPI, KOSDAQ, NYSE, NASDAQ)"
    )


class StockCreate(StockBase):
    pass


class StockUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Stock name")
    ticker: Optional[str] = Field(None, description="Stock ticker symbol")
    country: Optional[str] = Field(
        None, min_length=2, max_length=2, description="2-digit country code"
    )
    market: Optional[str] = Field(None, description="Market type")


class StockInDB(StockBase):
    id: str

    class Config:
        from_attributes = True


class Stock(StockInDB):
    pass
