"""
UserCardActivity Repository - 순수 데이터 접근 로직
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_card_activity import UserCardActivity
from app.models.card import Card


class UserCardActivityRepository:
    """활동 기록 데이터 접근 계층"""
    
    async def create(self, db: AsyncSession, activity: UserCardActivity) -> UserCardActivity:
        """활동 기록 생성"""
        db.add(activity)
        await db.commit()
        await db.refresh(activity)
        return activity
    
    async def get_by_id(
        self,
        db: AsyncSession,
        activity_id: UUID
    ) -> Optional[UserCardActivity]:
        """활동 기록 조회"""
        result = await db.execute(
            select(UserCardActivity).where(UserCardActivity.id == activity_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_activities(
        self,
        db: AsyncSession,
        userId: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> List[UserCardActivity]:
        """사용자 활동 목록 조회"""
        result = await db.execute(
            select(UserCardActivity)
            .where(UserCardActivity.userId == userId)
            .order_by(UserCardActivity.completedAt.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_user_activities_by_card(
        self,
        db: AsyncSession,
        userId: UUID,
        cardId: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> List[UserCardActivity]:
        """특정 카드에 대한 사용자 활동 목록 조회"""
        result = await db.execute(
            select(UserCardActivity)
            .where(
                UserCardActivity.userId == userId,
                UserCardActivity.cardId == cardId
            )
            .order_by(UserCardActivity.completedAt.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_count(
        self,
        db: AsyncSession,
        userId: UUID,
        cardId: Optional[UUID] = None,
    ) -> int:
        """사용자 활동 개수 조회"""
        query = select(func.count(UserCardActivity.id)).where(
            UserCardActivity.userId == userId
        )
        
        if cardId is not None:
            query = query.where(UserCardActivity.cardId == cardId)
        
        result = await db.execute(query)
        return result.scalar() or 0
    
    async def get_user_completed_cards(
        self,
        db: AsyncSession,
        userId: UUID,
        skip: int = 0,
        limit: int = 20,
        activityType: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """사용자가 활동한 카드 목록 조회 (중복 제거)"""
        subquery = (
            select(
                UserCardActivity.cardId,
                func.max(UserCardActivity.completedAt).label('lastActivityDate'),
                func.count(UserCardActivity.id).label('activityCount')
            )
            .where(UserCardActivity.userId == userId)
            .group_by(UserCardActivity.cardId)
            .subquery()
        )
        
        query = (
            select(
                Card.id,
                Card.title,
                Card.thumbnailUrl,
                Card.activityType,
                subquery.c.lastActivityDate,
                subquery.c.activityCount
            )
            .join(subquery, Card.id == subquery.c.cardId)
        )
        
        if activityType is not None:
            query = query.where(Card.activityType == activityType)
        
        query = query.order_by(subquery.c.lastActivityDate.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        rows = result.all()
        
        return [
            {
                "cardId": row.id,
                "title": row.title,
                "thumbnailUrl": row.thumbnailUrl,
                "activityType": row.activityType,
                "lastActivityDate": row.lastActivityDate,
                "activityCount": row.activityCount,
            }
            for row in rows
        ]
    
    async def get_recent_activities(
        self,
        db: AsyncSession,
        userId: UUID,
        days: int = 30,
        limit: int = 20,
    ) -> List[UserCardActivity]:
        """최근 N일 이내 활동 조회"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        result = await db.execute(
            select(UserCardActivity)
            .where(
                UserCardActivity.userId == userId,
                UserCardActivity.completedAt >= since_date
            )
            .order_by(UserCardActivity.completedAt.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_stats(
        self,
        db: AsyncSession,
        userId: UUID,
    ) -> Dict[str, Any]:
        """사용자 활동 통계 조회"""
        # 총 활동 수
        total_activities_result = await db.execute(
            select(func.count(UserCardActivity.id))
            .where(UserCardActivity.userId == userId)
        )
        total_activities = total_activities_result.scalar() or 0
        
        # 활동한 카드 수 (중복 제거)
        unique_cards_result = await db.execute(
            select(func.count(distinct(UserCardActivity.cardId)))
            .where(UserCardActivity.userId == userId)
        )
        unique_cards = unique_cards_result.scalar() or 0
        
        # 최근 활동 날짜
        recent_activity_result = await db.execute(
            select(func.max(UserCardActivity.completedAt))
            .where(UserCardActivity.userId == userId)
        )
        recent_activity_date = recent_activity_result.scalar()
        
        return {
            "totalActivities": total_activities,
            "uniqueCards": unique_cards,
            "recentActivityDate": recent_activity_date,
        }

