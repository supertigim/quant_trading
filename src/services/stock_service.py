from typing import List, Optional
from src.db.session import get_db
from src.db.repositories.stock import StockRepository
from src.models.stock import Stock
from src.schemas.stock import StockCreate, StockUpdate
from datetime import datetime


class StockService:
    def __init__(self):
        self.db = next(get_db())
        self.stock_repo = StockRepository(self.db)

    async def get_all_stocks(self) -> List[Stock]:
        """모든 주식 목록을 가져옵니다."""
        return self.stock_repo.get_all()

    async def get_stock_by_ticker(self, ticker: str) -> Optional[Stock]:
        """티커로 주식을 조회합니다."""
        return self.stock_repo.get_by_ticker(ticker)

    async def create_stock(self, stock: StockCreate) -> Stock:
        """새로운 주식을 생성합니다."""
        new_stock = Stock(
            ticker=stock.ticker,
            name=stock.name,
            country=stock.country,
            market=stock.market,
            currency=stock.currency,
            last_updated=datetime.now(),
        )
        return self.stock_repo.create(new_stock)

    async def update_stock(self, ticker: str, stock: StockUpdate) -> Optional[Stock]:
        """주식 정보를 업데이트합니다."""
        existing_stock = self.stock_repo.get_by_ticker(ticker)
        if not existing_stock:
            return None

        if stock.name is not None:
            existing_stock.name = stock.name
        if stock.country is not None:
            existing_stock.country = stock.country
        if stock.market is not None:
            existing_stock.market = stock.market
        if stock.currency is not None:
            existing_stock.currency = stock.currency

        existing_stock.last_updated = datetime.now()
        return self.stock_repo.update(existing_stock)

    async def delete_stock(self, ticker: str) -> bool:
        """주식을 삭제합니다."""
        stock = self.stock_repo.get_by_ticker(ticker)
        if not stock:
            return False
        self.stock_repo.delete(stock)
        return True
