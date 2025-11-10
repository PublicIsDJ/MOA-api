"""
Share Service - 비즈니스 로직
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.share import Share
from app.repositories.share import ShareRepository
from app.utils.token import generate_share_token
from app.utils.password import hash_password


class ShareService:
    """공유 링크 비즈니스 로직"""
    
    def __init__(self):
        self.repo = ShareRepository()
    
    async def create_share(
        self,
        db: AsyncSession,
        userId: UUID,
        cardId: UUID,
        password: Optional[str] = None,
        expiryDate: Optional[datetime] = None,
    ) -> Share:
        """
        공유 링크 생성
        
        비즈니스 로직:
        - 중복되지 않는 공유 토큰 생성
        - 비밀번호 해싱
        """
        # 공유 토큰 생성 (중복 체크)
        while True:
            shareToken = generate_share_token(16)
            existing = await self.repo.get_by_token(db, shareToken)
            if existing is None:
                break
        
        # 비밀번호 해싱
        hashed_password = hash_password(password) if password else None
        
        share = Share(
            userId=userId,
            cardId=cardId,
            shareToken=shareToken,
            password=hashed_password,
            expiryDate=expiryDate,
            viewCount=0,
            isActive=True,
        )
        
        return await self.repo.create(db, share)
    
    async def get_share_by_id(self, db: AsyncSession, share_id: UUID) -> Optional[Share]:
        """공유 링크 조회"""
        return await self.repo.get_by_id(db, share_id)
    
    async def get_share_by_token(self, db: AsyncSession, shareToken: str) -> Optional[Share]:
        """토큰으로 공유 링크 조회"""
        return await self.repo.get_by_token(db, shareToken)
    
    async def get_user_shares(
        self,
        db: AsyncSession,
        userId: UUID,
        skip: int = 0,
        limit: int = 20,
        isActive: Optional[bool] = None,
    ) -> List[Share]:
        """사용자 공유 목록 조회"""
        return await self.repo.get_user_shares(db, userId, skip, limit, isActive)
    
    async def get_card_shares(
        self,
        db: AsyncSession,
        cardId: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Share]:
        """카드 공유 목록 조회"""
        return await self.repo.get_card_shares(db, cardId, skip, limit)
    
    async def update_share(
        self,
        db: AsyncSession,
        share_id: UUID,
        **kwargs
    ) -> Optional[Share]:
        """
        공유 링크 수정
        
        비즈니스 로직:
        - 비밀번호 변경 시 해싱 처리
        """
        # 비밀번호 해싱 처리
        if 'password' in kwargs and kwargs['password'] is not None:
            kwargs['password'] = hash_password(kwargs['password'])
        
        return await self.repo.update(db, share_id, **kwargs)
    
    async def increment_view_count(
        self,
        db: AsyncSession,
        share_id: UUID
    ) -> Optional[Share]:
        """조회수 증가"""
        return await self.repo.increment_view_count(db, share_id)
    
    async def deactivate_share(
        self,
        db: AsyncSession,
        share_id: UUID
    ) -> Optional[Share]:
        """공유 링크 비활성화"""
        return await self.repo.deactivate(db, share_id)
    
    async def delete_share(
        self,
        db: AsyncSession,
        share_id: UUID
    ) -> bool:
        """공유 링크 완전 삭제"""
        return await self.repo.delete(db, share_id)
    
    def is_share_valid(self, share: Share) -> bool:
        """
        공유 링크 유효성 검증
        
        비즈니스 로직:
        - 비활성화 여부 확인
        - 만료일 확인
        """
        if not share.isActive:
            return False
        
        if share.expiryDate and share.expiryDate < datetime.utcnow():
            return False
        
        return True


# 싱글톤 인스턴스
share_service = ShareService()

