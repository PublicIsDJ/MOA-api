"""
User Repository - 순수 데이터 접근 로직
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.enums import SocialProviderType


class UserRepository:
    """사용자 데이터 접근 계층"""
    
    async def create(self, db: AsyncSession, user: User) -> User:
        """사용자 생성"""
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    async def get_by_id(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        """ID로 사용자 조회"""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_userId(self, db: AsyncSession, userId: str) -> Optional[User]:
        """userId로 사용자 조회"""
        result = await db.execute(
            select(User).where(User.userId == userId)
        )
        return result.scalar_one_or_none()
    
    async def get_by_social(
        self,
        db: AsyncSession,
        socialProvider: SocialProviderType,
        socialId: str
    ) -> Optional[User]:
        """소셜 로그인 정보로 사용자 조회"""
        result = await db.execute(
            select(User).where(
                User.socialProvider == socialProvider,
                User.socialId == socialId
            )
        )
        return result.scalar_one_or_none()
    
    async def update(
        self,
        db: AsyncSession,
        user_id: UUID,
        **kwargs
    ) -> Optional[User]:
        """사용자 정보 수정"""
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        
        if not update_data:
            return await self.get_by_id(db, user_id)
        
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
        )
        await db.commit()
        
        return await self.get_by_id(db, user_id)
    
    async def update_password(
        self,
        db: AsyncSession,
        user_id: UUID,
        hashed_password: str
    ) -> Optional[User]:
        """비밀번호 변경"""
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(password=hashed_password)
        )
        await db.commit()
        
        return await self.get_by_id(db, user_id)
    
    async def update_last_login(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> None:
        """마지막 로그인 시각 업데이트"""
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(lastLoginAt=datetime.utcnow())
        )
        await db.commit()
    
    async def deactivate(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> Optional[User]:
        """사용자 비활성화"""
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(isActive=False)
        )
        await db.commit()
        
        return await self.get_by_id(db, user_id)
    
    async def delete(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> bool:
        """사용자 완전 삭제"""
        user = await self.get_by_id(db, user_id)
        if user is None:
            return False
        
        await db.delete(user)
        await db.commit()
        
        return True

