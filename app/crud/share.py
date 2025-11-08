"""
Share CRUD 작업
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.share import Share
from app.utils.token import generate_share_token
from app.utils.password import hash_password


async def create_share(
    db: AsyncSession,
    userId: UUID,
    cardId: UUID,
    password: Optional[str] = None,
    expiryDate: Optional[datetime] = None,
) -> Share:
    """
    공유 링크 생성
    
    Args:
        db: 데이터베이스 세션
        userId: 사용자 ID
        cardId: 카드 ID
        password: 비밀번호 (선택)
        expiryDate: 만료일 (선택)
    
    Returns:
        Share: 생성된 공유 링크 객체
    """
    # 공유 토큰 생성 (중복 체크)
    while True:
        shareToken = generate_share_token(16)
        existing = await get_share_by_token(db, shareToken)
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
    
    db.add(share)
    await db.commit()
    await db.refresh(share)
    
    return share


async def get_share_by_id(db: AsyncSession, share_id: UUID) -> Optional[Share]:
    """
    공유 링크 조회
    
    Args:
        db: 데이터베이스 세션
        share_id: 공유 링크 ID
    
    Returns:
        Optional[Share]: 공유 링크 객체 또는 None
    """
    result = await db.execute(
        select(Share).where(Share.id == share_id)
    )
    return result.scalar_one_or_none()


async def get_share_by_token(db: AsyncSession, shareToken: str) -> Optional[Share]:
    """
    토큰으로 공유 링크 조회
    
    Args:
        db: 데이터베이스 세션
        shareToken: 공유 토큰
    
    Returns:
        Optional[Share]: 공유 링크 객체 또는 None
    """
    result = await db.execute(
        select(Share).where(Share.shareToken == shareToken)
    )
    return result.scalar_one_or_none()


async def get_user_shares(
    db: AsyncSession,
    userId: UUID,
    skip: int = 0,
    limit: int = 20,
    isActive: Optional[bool] = None,
) -> List[Share]:
    """
    사용자 공유 목록 조회
    
    Args:
        db: 데이터베이스 세션
        userId: 사용자 ID
        skip: 건너뛸 개수
        limit: 조회할 개수
        isActive: 활성화 여부 필터
    
    Returns:
        List[Share]: 공유 링크 목록
    """
    query = select(Share).where(Share.userId == userId)
    
    if isActive is not None:
        query = query.where(Share.isActive == isActive)
    
    query = query.order_by(Share.createdAt.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_card_shares(
    db: AsyncSession,
    cardId: UUID,
    skip: int = 0,
    limit: int = 20,
) -> List[Share]:
    """
    카드 공유 목록 조회
    
    Args:
        db: 데이터베이스 세션
        cardId: 카드 ID
        skip: 건너뛸 개수
        limit: 조회할 개수
    
    Returns:
        List[Share]: 공유 링크 목록
    """
    result = await db.execute(
        select(Share)
        .where(Share.cardId == cardId)
        .order_by(Share.createdAt.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def update_share(
    db: AsyncSession,
    share_id: UUID,
    **kwargs
) -> Optional[Share]:
    """
    공유 링크 수정
    
    Args:
        db: 데이터베이스 세션
        share_id: 공유 링크 ID
        **kwargs: 수정할 필드 (password, expiryDate, isActive 등)
    
    Returns:
        Optional[Share]: 수정된 공유 링크 객체 또는 None
    """
    # 비밀번호 해싱 처리
    if 'password' in kwargs and kwargs['password'] is not None:
        kwargs['password'] = hash_password(kwargs['password'])
    
    # 수정할 데이터 필터링
    update_data = {k: v for k, v in kwargs.items() if v is not None}
    
    if not update_data:
        return await get_share_by_id(db, share_id)
    
    # 업데이트 실행
    await db.execute(
        update(Share)
        .where(Share.id == share_id)
        .values(**update_data)
    )
    await db.commit()
    
    return await get_share_by_id(db, share_id)


async def increment_view_count(
    db: AsyncSession,
    share_id: UUID
) -> Optional[Share]:
    """
    조회수 증가
    
    Args:
        db: 데이터베이스 세션
        share_id: 공유 링크 ID
    
    Returns:
        Optional[Share]: 수정된 공유 링크 객체 또는 None
    """
    await db.execute(
        update(Share)
        .where(Share.id == share_id)
        .values(viewCount=Share.viewCount + 1)
    )
    await db.commit()
    
    return await get_share_by_id(db, share_id)


async def deactivate_share(
    db: AsyncSession,
    share_id: UUID
) -> Optional[Share]:
    """
    공유 링크 비활성화
    
    Args:
        db: 데이터베이스 세션
        share_id: 공유 링크 ID
    
    Returns:
        Optional[Share]: 비활성화된 공유 링크 객체 또는 None
    """
    await db.execute(
        update(Share)
        .where(Share.id == share_id)
        .values(isActive=False)
    )
    await db.commit()
    
    return await get_share_by_id(db, share_id)


async def delete_share(
    db: AsyncSession,
    share_id: UUID
) -> bool:
    """
    공유 링크 완전 삭제
    
    Args:
        db: 데이터베이스 세션
        share_id: 공유 링크 ID
    
    Returns:
        bool: 삭제 성공 여부
    """
    share = await get_share_by_id(db, share_id)
    if share is None:
        return False
    
    await db.delete(share)
    await db.commit()
    
    return True


async def is_share_valid(share: Share) -> bool:
    """
    공유 링크 유효성 검증
    
    Args:
        share: 공유 링크 객체
    
    Returns:
        bool: 유효 여부
    """
    # 비활성화된 경우
    if not share.isActive:
        return False
    
    # 만료일이 지난 경우
    if share.expiryDate and share.expiryDate < datetime.utcnow():
        return False
    
    return True

