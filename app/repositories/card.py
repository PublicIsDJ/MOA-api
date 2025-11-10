"""
Card Repository - 순수 데이터 접근 로직
"""
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.card import Card


class CardRepository:
    """카드 데이터 접근 계층"""
    
    async def create(self, db: AsyncSession, card: Card) -> Card:
        """카드 생성"""
        db.add(card)
        await db.commit()
        await db.refresh(card)
        return card
    
    async def get_by_id(self, db: AsyncSession, card_id: UUID) -> Optional[Card]:
        """ID로 카드 조회"""
        result = await db.execute(
            select(Card).where(Card.id == card_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_qr_code(self, db: AsyncSession, qrCode: str) -> Optional[Card]:
        """QR 코드로 카드 조회"""
        result = await db.execute(
            select(Card).where(Card.qrCode == qrCode)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        activityType: Optional[str] = None,
        isActive: Optional[bool] = None,
    ) -> List[Card]:
        """카드 목록 조회"""
        query = select(Card)
        
        if activityType is not None:
            query = query.where(Card.activityType == activityType)
        
        if isActive is not None:
            query = query.where(Card.isActive == isActive)
        
        query = query.order_by(Card.createdAt.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_count(
        self,
        db: AsyncSession,
        activityType: Optional[str] = None,
        isActive: Optional[bool] = None,
    ) -> int:
        """카드 총 개수 조회"""
        query = select(func.count(Card.id))
        
        if activityType is not None:
            query = query.where(Card.activityType == activityType)
        
        if isActive is not None:
            query = query.where(Card.isActive == isActive)
        
        result = await db.execute(query)
        return result.scalar() or 0
    
    async def update(
        self,
        db: AsyncSession,
        card_id: UUID,
        **kwargs
    ) -> Optional[Card]:
        """카드 정보 수정"""
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        
        if not update_data:
            return await self.get_by_id(db, card_id)
        
        await db.execute(
            update(Card)
            .where(Card.id == card_id)
            .values(**update_data)
        )
        await db.commit()
        
        return await self.get_by_id(db, card_id)
    
    async def deactivate(
        self,
        db: AsyncSession,
        card_id: UUID
    ) -> Optional[Card]:
        """카드 비활성화"""
        await db.execute(
            update(Card)
            .where(Card.id == card_id)
            .values(isActive=False)
        )
        await db.commit()
        
        return await self.get_by_id(db, card_id)
    
    async def delete(
        self,
        db: AsyncSession,
        card_id: UUID
    ) -> bool:
        """카드 완전 삭제"""
        card = await self.get_by_id(db, card_id)
        if card is None:
            return False
        
        await db.delete(card)
        await db.commit()
        
        return True
    
    async def get_active_cards(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        activityType: Optional[str] = None,
    ) -> List[Card]:
        """활성화된 카드 목록 조회"""
        return await self.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            activityType=activityType,
            isActive=True
        )

