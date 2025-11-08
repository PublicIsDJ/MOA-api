"""
Card CRUD 작업
"""
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.card import Card


async def create_card(
    db: AsyncSession,
    qrCode: str,
    title: str,
    activityType: str,
    activityData: dict,
    description: Optional[str] = None,
    thumbnailUrl: Optional[str] = None,
    isActive: bool = True,
) -> Card:
    """
    카드 생성 (관리자용)
    
    Args:
        db: 데이터베이스 세션
        qrCode: QR 코드
        title: 카드 제목
        activityType: 활동 타입
        activityData: 활동 데이터 (JSONB)
        description: 카드 설명
        thumbnailUrl: 썸네일 URL
        isActive: 활성화 여부
    
    Returns:
        Card: 생성된 카드 객체
    """
    card = Card(
        qrCode=qrCode,
        title=title,
        description=description,
        activityType=activityType,
        activityData=activityData,
        thumbnailUrl=thumbnailUrl,
        isActive=isActive,
    )
    
    db.add(card)
    await db.commit()
    await db.refresh(card)
    
    return card


async def get_card_by_id(db: AsyncSession, card_id: UUID) -> Optional[Card]:
    """
    ID로 카드 조회
    
    Args:
        db: 데이터베이스 세션
        card_id: 카드 ID
    
    Returns:
        Optional[Card]: 카드 객체 또는 None
    """
    result = await db.execute(
        select(Card).where(Card.id == card_id)
    )
    return result.scalar_one_or_none()


async def get_card_by_qr_code(db: AsyncSession, qrCode: str) -> Optional[Card]:
    """
    QR 코드로 카드 조회
    
    Args:
        db: 데이터베이스 세션
        qrCode: QR 코드
    
    Returns:
        Optional[Card]: 카드 객체 또는 None
    """
    result = await db.execute(
        select(Card).where(Card.qrCode == qrCode)
    )
    return result.scalar_one_or_none()


async def get_cards(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    activityType: Optional[str] = None,
    isActive: Optional[bool] = None,
) -> List[Card]:
    """
    카드 목록 조회 (페이지네이션)
    
    Args:
        db: 데이터베이스 세션
        skip: 건너뛸 개수
        limit: 조회할 개수
        activityType: 활동 타입 필터
        isActive: 활성화 여부 필터
    
    Returns:
        List[Card]: 카드 목록
    """
    query = select(Card)
    
    # 필터 적용
    if activityType is not None:
        query = query.where(Card.activityType == activityType)
    
    if isActive is not None:
        query = query.where(Card.isActive == isActive)
    
    # 정렬 및 페이지네이션
    query = query.order_by(Card.createdAt.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_cards_count(
    db: AsyncSession,
    activityType: Optional[str] = None,
    isActive: Optional[bool] = None,
) -> int:
    """
    카드 총 개수 조회
    
    Args:
        db: 데이터베이스 세션
        activityType: 활동 타입 필터
        isActive: 활성화 여부 필터
    
    Returns:
        int: 카드 총 개수
    """
    query = select(func.count(Card.id))
    
    # 필터 적용
    if activityType is not None:
        query = query.where(Card.activityType == activityType)
    
    if isActive is not None:
        query = query.where(Card.isActive == isActive)
    
    result = await db.execute(query)
    return result.scalar() or 0


async def update_card(
    db: AsyncSession,
    card_id: UUID,
    **kwargs
) -> Optional[Card]:
    """
    카드 정보 수정
    
    Args:
        db: 데이터베이스 세션
        card_id: 카드 ID
        **kwargs: 수정할 필드 (title, description, activityType, activityData, thumbnailUrl, isActive 등)
    
    Returns:
        Optional[Card]: 수정된 카드 객체 또는 None
    """
    # 수정할 데이터 필터링 (None이 아닌 값만)
    update_data = {k: v for k, v in kwargs.items() if v is not None}
    
    if not update_data:
        return await get_card_by_id(db, card_id)
    
    # 업데이트 실행
    await db.execute(
        update(Card)
        .where(Card.id == card_id)
        .values(**update_data)
    )
    await db.commit()
    
    # 수정된 카드 조회
    return await get_card_by_id(db, card_id)


async def deactivate_card(
    db: AsyncSession,
    card_id: UUID
) -> Optional[Card]:
    """
    카드 비활성화
    
    Args:
        db: 데이터베이스 세션
        card_id: 카드 ID
    
    Returns:
        Optional[Card]: 비활성화된 카드 객체 또는 None
    """
    await db.execute(
        update(Card)
        .where(Card.id == card_id)
        .values(isActive=False)
    )
    await db.commit()
    
    return await get_card_by_id(db, card_id)


async def delete_card(
    db: AsyncSession,
    card_id: UUID
) -> bool:
    """
    카드 완전 삭제
    
    Args:
        db: 데이터베이스 세션
        card_id: 카드 ID
    
    Returns:
        bool: 삭제 성공 여부
    """
    card = await get_card_by_id(db, card_id)
    if card is None:
        return False
    
    await db.delete(card)
    await db.commit()
    
    return True


async def get_active_cards(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    activityType: Optional[str] = None,
) -> List[Card]:
    """
    활성화된 카드 목록 조회
    
    Args:
        db: 데이터베이스 세션
        skip: 건너뛸 개수
        limit: 조회할 개수
        activityType: 활동 타입 필터
    
    Returns:
        List[Card]: 활성화된 카드 목록
    """
    return await get_cards(
        db=db,
        skip=skip,
        limit=limit,
        activityType=activityType,
        isActive=True
    )

