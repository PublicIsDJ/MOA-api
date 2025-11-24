"""
UserCardActivity Service - 비즈니스 로직
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_card_activity import UserCardActivity
from app.repositories.user_card_activity import UserCardActivityRepository


class UserCardActivityService:
    """활동 기록 비즈니스 로직"""
    
    def __init__(self):
        self.repo = UserCardActivityRepository()
    
    async def create_activity(
        self,
        db: AsyncSession,
        userId: UUID,
        cardId: UUID,
        activityResult: dict,
    ) -> UserCardActivity:
        """
        활동 기록 생성
        
        비즈니스 로직:
        - 완료 시각 자동 설정
        """
        activity = UserCardActivity(
            userId=userId,
            cardId=cardId,
            activityResult=activityResult,
            completedAt=datetime.utcnow(),
        )
        
        return await self.repo.create(db, activity)
    
    async def create_activity_with_validation(
        self,
        db: AsyncSession,
        userId: UUID,
        cardId: UUID,
        activityResult: dict,
    ) -> UserCardActivity:
        """
        활동 기록 생성 (검증 포함)
        
        비즈니스 로직:
        - 카드 존재 여부 확인
        - 카드 활성화 상태 확인
        - 활동 기록 생성
        
        Raises:
            HTTPException: 카드를 찾을 수 없거나 비활성화된 경우
        """
        from fastapi import HTTPException, status
        from app.services.card import card_service

        # 카드 존재 여부 확인
        card = await card_service.get_card_by_id(db, cardId)
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="카드를 찾을 수 없습니다"
            )
        
        # 비활성 카드는 활동 불가
        if not card.isActive:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비활성화된 카드입니다"
            )
        
        # 활동 기록 생성
        return await self.create_activity(db, userId, cardId, activityResult)
    
    async def get_activity_by_id(
        self,
        db: AsyncSession,
        activity_id: UUID
    ) -> Optional[UserCardActivity]:
        """활동 기록 조회"""
        return await self.repo.get_by_id(db, activity_id)
    
    async def get_activity_with_permission_check(
        self,
        db: AsyncSession,
        activity_id: UUID,
        userId: UUID
    ) -> UserCardActivity:
        """
        활동 기록 조회 (권한 확인 포함)
        
        비즈니스 로직:
        - 활동 기록 존재 여부 확인
        - 본인의 활동인지 권한 확인
        
        Raises:
            HTTPException: 활동을 찾을 수 없거나 권한이 없는 경우
        """
        from fastapi import HTTPException, status

        activity = await self.repo.get_by_id(db, activity_id)

        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="활동 기록을 찾을 수 없습니다"
            )
        
        # 본인의 활동만 조회 가능
        if activity.userId != userId:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="접근 권한이 없습니다"
            )
        
        return activity
    
    async def get_user_activities(
        self,
        db: AsyncSession,
        userId: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> List[UserCardActivity]:
        """사용자 활동 목록 조회"""
        return await self.repo.get_user_activities(db, userId, skip, limit)
    
    async def get_user_activities_by_card(
        self,
        db: AsyncSession,
        userId: UUID,
        cardId: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> List[UserCardActivity]:
        """특정 카드에 대한 사용자 활동 목록 조회"""
        return await self.repo.get_user_activities_by_card(db, userId, cardId, skip, limit)
    
    async def get_user_activities_count(
        self,
        db: AsyncSession,
        userId: UUID,
        cardId: Optional[UUID] = None,
    ) -> int:
        """사용자 활동 개수 조회"""
        return await self.repo.get_count(db, userId, cardId)
    
    async def get_user_completed_cards(
        self,
        db: AsyncSession,
        userId: UUID,
        skip: int = 0,
        limit: int = 20,
        activityType: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """사용자가 활동한 카드 목록 조회 (중복 제거)"""
        return await self.repo.get_user_completed_cards(db, userId, skip, limit, activityType)
    
    async def get_recent_activities(
        self,
        db: AsyncSession,
        userId: UUID,
        days: int = 30,
        limit: int = 20,
    ) -> List[UserCardActivity]:
        """최근 N일 이내 활동 조회"""
        return await self.repo.get_recent_activities(db, userId, days, limit)
    
    async def get_activity_stats(
        self,
        db: AsyncSession,
        userId: UUID,
    ) -> Dict[str, Any]:
        """사용자 활동 통계 조회"""
        return await self.repo.get_stats(db, userId)


# 싱글톤 인스턴스
user_card_activity_service = UserCardActivityService()

