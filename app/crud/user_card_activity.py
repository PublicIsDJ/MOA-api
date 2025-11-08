"""
UserCardActivity CRUD 작업
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_card_activity import UserCardActivity
from app.models.card import Card


async def create_activity(
    db: AsyncSession,
    userId: UUID,
    cardId: UUID,
    activityResult: dict,
) -> UserCardActivity:
    """
    활동 기록 생성
    
    Args:
        db: 데이터베이스 세션
        userId: 사용자 ID
        cardId: 카드 ID
        activityResult: 활동 결과 데이터 (JSONB)
    
    Returns:
        UserCardActivity: 생성된 활동 기록 객체
    """
    activity = UserCardActivity(
        userId=userId,
        cardId=cardId,
        activityResult=activityResult,
        completedAt=datetime.utcnow(),
    )
    
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    
    return activity


async def get_activity_by_id(
    db: AsyncSession,
    activity_id: UUID
) -> Optional[UserCardActivity]:
    """
    활동 기록 조회
    
    Args:
        db: 데이터베이스 세션
        activity_id: 활동 기록 ID
    
    Returns:
        Optional[UserCardActivity]: 활동 기록 객체 또는 None
    """
    result = await db.execute(
        select(UserCardActivity).where(UserCardActivity.id == activity_id)
    )
    return result.scalar_one_or_none()


async def get_user_activities(
    db: AsyncSession,
    userId: UUID,
    skip: int = 0,
    limit: int = 20,
) -> List[UserCardActivity]:
    """
    사용자 활동 목록 조회
    
    Args:
        db: 데이터베이스 세션
        userId: 사용자 ID
        skip: 건너뛸 개수
        limit: 조회할 개수
    
    Returns:
        List[UserCardActivity]: 활동 기록 목록
    """
    result = await db.execute(
        select(UserCardActivity)
        .where(UserCardActivity.userId == userId)
        .order_by(UserCardActivity.completedAt.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_user_activities_by_card(
    db: AsyncSession,
    userId: UUID,
    cardId: UUID,
    skip: int = 0,
    limit: int = 20,
) -> List[UserCardActivity]:
    """
    특정 카드에 대한 사용자 활동 목록 조회
    
    Args:
        db: 데이터베이스 세션
        userId: 사용자 ID
        cardId: 카드 ID
        skip: 건너뛸 개수
        limit: 조회할 개수
    
    Returns:
        List[UserCardActivity]: 활동 기록 목록
    """
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


async def get_user_activities_count(
    db: AsyncSession,
    userId: UUID,
    cardId: Optional[UUID] = None,
) -> int:
    """
    사용자 활동 개수 조회
    
    Args:
        db: 데이터베이스 세션
        userId: 사용자 ID
        cardId: 카드 ID (선택)
    
    Returns:
        int: 활동 개수
    """
    query = select(func.count(UserCardActivity.id)).where(
        UserCardActivity.userId == userId
    )
    
    if cardId is not None:
        query = query.where(UserCardActivity.cardId == cardId)
    
    result = await db.execute(query)
    return result.scalar() or 0


async def get_user_completed_cards(
    db: AsyncSession,
    userId: UUID,
    skip: int = 0,
    limit: int = 20,
    activityType: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    사용자가 활동한 카드 목록 조회 (중복 제거)
    
    Args:
        db: 데이터베이스 세션
        userId: 사용자 ID
        skip: 건너뛸 개수
        limit: 조회할 개수
        activityType: 활동 타입 필터
    
    Returns:
        List[Dict]: 카드 정보 + 마지막 활동 시각 + 활동 횟수
    """
    # 서브쿼리: 각 카드별 마지막 활동 시각과 활동 횟수
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
    
    # 메인 쿼리: 카드 정보와 조인
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
    
    # 활동 타입 필터
    if activityType is not None:
        query = query.where(Card.activityType == activityType)
    
    # 정렬 및 페이지네이션
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
    db: AsyncSession,
    userId: UUID,
    days: int = 30,
    limit: int = 20,
) -> List[UserCardActivity]:
    """
    최근 N일 이내 활동 조회
    
    Args:
        db: 데이터베이스 세션
        userId: 사용자 ID
        days: 조회할 일수
        limit: 조회할 개수
    
    Returns:
        List[UserCardActivity]: 활동 기록 목록
    """
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


async def get_activity_stats(
    db: AsyncSession,
    userId: UUID,
) -> Dict[str, Any]:
    """
    사용자 활동 통계 조회
    
    Args:
        db: 데이터베이스 세션
        userId: 사용자 ID
    
    Returns:
        Dict: 활동 통계 (총 활동 수, 활동한 카드 수, 최근 활동 날짜 등)
    """
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

