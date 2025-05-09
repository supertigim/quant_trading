from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.core.security import get_password_hash
import uuid


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[User]:
        """모든 사용자를 가져옵니다."""
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """ID로 사용자를 조회합니다."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자를 조회합니다."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """사용자 이름으로 사용자를 조회합니다."""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, user_in: UserCreate) -> User:
        """새로운 사용자를 생성합니다."""
        db_user = User(
            id=str(uuid.uuid4()),
            email=user_in.email,
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
            is_active=True,
            is_superuser=False,
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def update(self, user: User, user_in: UserUpdate) -> User:
        """사용자 정보를 업데이트합니다."""
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(
                update_data.pop("password")
            )
        for field, value in update_data.items():
            setattr(user, field, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        """사용자를 삭제합니다."""
        await self.db.delete(user)
        await self.db.commit()
