from typing import Optional, List
from sqlalchemy.orm import Session
from src.models.stock import Stock
from src.schemas.stock import StockCreate, StockUpdate
import uuid


class StockRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, stock_id: str) -> Optional[Stock]:
        return self.db.query(Stock).filter(Stock.id == stock_id).first()

    def get_by_ticker(self, ticker: str) -> Optional[Stock]:
        return self.db.query(Stock).filter(Stock.ticker == ticker).first()

    def get_by_country(self, country: str) -> List[Stock]:
        return self.db.query(Stock).filter(Stock.country == country).all()

    def get_all(self) -> List[Stock]:
        return self.db.query(Stock).all()

    def create(self, stock_in: StockCreate) -> Stock:
        db_stock = Stock(
            id=str(uuid.uuid4()),
            name=stock_in.name,
            ticker=stock_in.ticker,
            country=stock_in.country,
        )
        self.db.add(db_stock)
        self.db.commit()
        self.db.refresh(db_stock)
        return db_stock

    def update(self, stock: Stock, stock_in: StockUpdate) -> Stock:
        update_data = stock_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(stock, field, value)
        self.db.add(stock)
        self.db.commit()
        self.db.refresh(stock)
        return stock

    def delete(self, stock: Stock) -> None:
        self.db.delete(stock)
        self.db.commit()
