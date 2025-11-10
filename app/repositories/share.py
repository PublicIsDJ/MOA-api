"""
Share Repository - 순수 데이터 접근 로직
"""
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.share import Share


class ShareRepository:
    """공유 링크 데이터 접근 계층"""
    
    async def create(self, db: AsyncSession, share: Share) -> Share:
        """공유 링크 생성"""
        db.add(share)
        await db.commit()
        await db.refresh(share)
        return share
    
    async def get_by_id(self, db: AsyncSession, share_id: UUID) -> Optional[Share]:
        """공유 링크 조회"""
        result = await db.execute(
            select(Share).where(Share.id == share_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_token(self, db: AsyncSession, shareToken: str) -> Optional[Share]:
        """토큰으로 공유 링크 조회"""
        result = await db.execute(
            select(Share).where(Share.shareToken == shareToken)
        )
        return result.scalar_one_or_none()
    
    async def get_user_shares(
        self,
        db: AsyncSession,
        userId: UUID,
        skip: int = 0,
        limit: int = 20,
        isActive: Optional[bool] = None,
    ) -> List[Share]:
        """사용자 공유 목록 조회"""
        query = select(Share).where(Share.userId == userId)
        
        if isActive is not None:
            query = query.where(Share.isActive == isActive)
        
        query = query.order_by(Share.createdAt.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_card_shares(
        self,
        db: AsyncSession,
        cardId: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Share]:
        """카드 공유 목록 조회"""
        result = await db.execute(
            select(Share)
            .where(Share.cardId == cardId)
            .order_by(Share.createdAt.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def update(
        self,
        db: AsyncSession,
        share_id: UUID,
        **kwargs
    ) -> Optional[Share]:
        """공유 링크 수정"""
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        
        if not update_data:
            return await self.get_by_id(db, share_id)
        
        await db.execute(
            update(Share)
            .where(Share.id == share_id)
            .values(**update_data)
        )
        await db.commit()
        
        return await self.get_by_id(db, share_id)
    
    async def increment_view_count(
        self,
        db: AsyncSession,
        share_id: UUID
    ) -> Optional[Share]:
        """조회수 증가"""
        await db.execute(
            update(Share)
            .where(Share.id == share_id)
            .values(viewCount=Share.viewCount + 1)
        )
        await db.commit()
        
        return await self.get_by_id(db, share_id)
    
    async def deactivate(
        self,
        db: AsyncSession,
        share_id: UUID
    ) -> Optional[Share]:
        """공유 링크 비활성화"""
        await db.execute(
            update(Share)
            .where(Share.id == share_id)
            .values(isActive=False)
        )
        await db.commit()
        
        return await self.get_by_id(db, share_id)
    
    async def delete(
        self,
        db: AsyncSession,
        share_id: UUID
    ) -> bool:
        """공유 링크 완전 삭제"""
        share = await self.get_by_id(db, share_id)
        if share is None:
            return False
        
        await db.delete(share)
        await db.commit()
        
        return True

