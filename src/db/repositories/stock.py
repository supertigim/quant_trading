from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.stock import Stock
from typing import List, Optional
from uuid import UUID


class StockRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Stock]:
        """모든 주식 목록을 가져옵니다."""
        result = await self.db.execute(select(Stock))
        return result.scalars().all()

    async def get_by_id(self, stock_id: UUID) -> Optional[Stock]:
        """ID로 주식을 조회합니다."""
        result = await self.db.execute(select(Stock).where(Stock.id == stock_id))
        return result.scalar_one_or_none()

    async def get_by_ticker(self, ticker: str) -> Optional[Stock]:
        """티커로 주식을 조회합니다."""
        result = await self.db.execute(select(Stock).where(Stock.ticker == ticker))
        return result.scalar_one_or_none()

    async def create(self, stock: Stock) -> Stock:
        """새로운 주식을 생성합니다."""
        self.db.add(stock)
        await self.db.commit()
        await self.db.refresh(stock)
        return stock

    async def update(self, stock: Stock) -> Stock:
        """주식 정보를 업데이트합니다."""
        await self.db.commit()
        await self.db.refresh(stock)
        return stock

    async def delete(self, stock_id: UUID) -> bool:
        """주식을 삭제합니다."""
        stock = await self.get_by_id(stock_id)
        if stock:
            await self.db.delete(stock)
            await self.db.commit()
            return True
        return False
