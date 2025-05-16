from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.price import Price


class PriceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, price: Price) -> Price:
        """가격 데이터 생성"""
        self.session.add(price)
        await self.session.commit()
        await self.session.refresh(price)
        return price

    async def get_by_id(self, price_id: int) -> Optional[Price]:
        """ID로 가격 데이터 조회"""
        result = await self.session.execute(select(Price).where(Price.id == price_id))
        return result.scalar_one_or_none()

    async def get_by_stock_and_date(
        self, stock_id: int, date: datetime
    ) -> Optional[Price]:
        """주식 ID와 날짜로 가격 데이터 조회"""
        result = await self.session.execute(
            select(Price).where(Price.stock_id == stock_id, Price.date == date)
        )
        return result.scalar_one_or_none()

    async def get_by_stock_and_date_range(
        self, stock_id: int, start_date: datetime, end_date: datetime
    ) -> List[Price]:
        """주식 ID와 날짜 범위로 가격 데이터 조회"""
        result = await self.session.execute(
            select(Price)
            .where(
                Price.stock_id == stock_id,
                Price.date >= start_date,
                Price.date <= end_date,
            )
            .order_by(Price.date)
        )
        return result.scalars().all()

    async def update(self, price: Price) -> Price:
        """가격 데이터 업데이트"""
        await self.session.commit()
        await self.session.refresh(price)
        return price

    async def delete(self, price: Price) -> None:
        """가격 데이터 삭제"""
        await self.session.delete(price)
        await self.session.commit()

    async def bulk_create(self, prices: List[Price]) -> List[Price]:
        """여러 주식 가격 데이터를 한 번에 생성합니다."""
        self.session.add_all(prices)
        await self.session.commit()
        for price in prices:
            await self.session.refresh(price)
        return prices
