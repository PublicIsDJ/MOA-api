"""
Card Service - 비즈니스 로직
"""
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.card import Card
from app.repositories.card import CardRepository


class CardService:
    """카드 비즈니스 로직"""
    
    def __init__(self):
        self.repo = CardRepository()
    
    async def create_card(
        self,
        db: AsyncSession,
        qrCode: str,
        title: str,
        activityType: str,
        activityData: dict,
        description: Optional[str] = None,
        thumbnailUrl: Optional[str] = None,
        isActive: bool = True,
    ) -> Card:
        """카드 생성 (관리자용)"""
        card = Card(
            qrCode=qrCode,
            title=title,
            description=description,
            activityType=activityType,
            activityData=activityData,
            thumbnailUrl=thumbnailUrl,
            isActive=isActive,
        )
        
        return await self.repo.create(db, card)
    
    async def get_card_by_id(self, db: AsyncSession, card_id: UUID) -> Optional[Card]:
        """ID로 카드 조회"""
        return await self.repo.get_by_id(db, card_id)
    
    async def get_card_by_qr_code(self, db: AsyncSession, qrCode: str) -> Optional[Card]:
        """QR 코드로 카드 조회"""
        return await self.repo.get_by_qr_code(db, qrCode)
    
    async def get_cards(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        activityType: Optional[str] = None,
        isActive: Optional[bool] = None,
    ) -> List[Card]:
        """카드 목록 조회"""
        return await self.repo.get_multi(db, skip, limit, activityType, isActive)
    
    async def get_cards_count(
        self,
        db: AsyncSession,
        activityType: Optional[str] = None,
        isActive: Optional[bool] = None,
    ) -> int:
        """카드 총 개수 조회"""
        return await self.repo.get_count(db, activityType, isActive)
    
    async def update_card(
        self,
        db: AsyncSession,
        card_id: UUID,
        **kwargs
    ) -> Optional[Card]:
        """카드 정보 수정"""
        return await self.repo.update(db, card_id, **kwargs)
    
    async def deactivate_card(
        self,
        db: AsyncSession,
        card_id: UUID
    ) -> Optional[Card]:
        """카드 비활성화"""
        return await self.repo.deactivate(db, card_id)
    
    async def delete_card(
        self,
        db: AsyncSession,
        card_id: UUID
    ) -> bool:
        """카드 완전 삭제"""
        return await self.repo.delete(db, card_id)
    
    async def get_active_cards(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        activityType: Optional[str] = None,
    ) -> List[Card]:
        """활성화된 카드 목록 조회"""
        return await self.repo.get_active_cards(db, skip, limit, activityType)


# 싱글톤 인스턴스
card_service = CardService()

