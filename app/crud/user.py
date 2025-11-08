"""
User CRUD 작업
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.enums import SocialProviderType
from app.utils.password import hash_password


async def create_user(
    db: AsyncSession,
    userId: str,
    password: str,
    userName: str,
    gender: Optional[str] = None,
    interest: Optional[str] = None,
    phoneNumber: Optional[str] = None,
) -> User:
    """
    일반 회원가입으로 사용자 생성
    
    Args:
        db: 데이터베이스 세션
        userId: 로그인 ID
        password: 비밀번호 (평문)
        userName: 사용자 이름
        gender: 성별
        interest: 관심사
        phoneNumber: 전화번호
    
    Returns:
        User: 생성된 사용자 객체
    """
    # 비밀번호 해싱
    hashed_password = hash_password(password)
    
    # 사용자 생성
    user = User(
        userId=userId,
        password=hashed_password,
        userName=userName,
        gender=gender,
        interest=interest,
        phoneNumber=phoneNumber,
        isActive=True,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


async def create_social_user(
    db: AsyncSession,
    userId: str,
    userName: str,
    socialProvider: SocialProviderType,
    socialId: str,
    gender: Optional[str] = None,
    interest: Optional[str] = None,
    phoneNumber: Optional[str] = None,
    profileImageUrl: Optional[str] = None,
) -> User:
    """
    소셜 로그인으로 사용자 생성
    
    Args:
        db: 데이터베이스 세션
        userId: 로그인 ID (소셜 이메일 등)
        userName: 사용자 이름
        socialProvider: 소셜 제공자 (kakao)
        socialId: 소셜 고유 ID
        gender: 성별
        interest: 관심사
        phoneNumber: 전화번호
        profileImageUrl: 프로필 이미지 URL
    
    Returns:
        User: 생성된 사용자 객체
    """
    user = User(
        userId=userId,
        password=None,  # 소셜 로그인은 비밀번호 없음
        userName=userName,
        socialProvider=socialProvider,
        socialId=socialId,
        gender=gender,
        interest=interest,
        phoneNumber=phoneNumber,
        profileImageUrl=profileImageUrl,
        isActive=True,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """
    ID로 사용자 조회
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID (UUID)
    
    Returns:
        Optional[User]: 사용자 객체 또는 None
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_userId(db: AsyncSession, userId: str) -> Optional[User]:
    """
    userId로 사용자 조회
    
    Args:
        db: 데이터베이스 세션
        userId: 로그인 ID
    
    Returns:
        Optional[User]: 사용자 객체 또는 None
    """
    result = await db.execute(
        select(User).where(User.userId == userId)
    )
    return result.scalar_one_or_none()


async def get_user_by_social(
    db: AsyncSession,
    socialProvider: SocialProviderType,
    socialId: str
) -> Optional[User]:
    """
    소셜 로그인 정보로 사용자 조회
    
    Args:
        db: 데이터베이스 세션
        socialProvider: 소셜 제공자
        socialId: 소셜 고유 ID
    
    Returns:
        Optional[User]: 사용자 객체 또는 None
    """
    result = await db.execute(
        select(User).where(
            User.socialProvider == socialProvider,
            User.socialId == socialId
        )
    )
    return result.scalar_one_or_none()


async def update_user(
    db: AsyncSession,
    user_id: UUID,
    **kwargs
) -> Optional[User]:
    """
    사용자 정보 수정
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        **kwargs: 수정할 필드 (userName, gender, interest, phoneNumber, profileImageUrl 등)
    
    Returns:
        Optional[User]: 수정된 사용자 객체 또는 None
    """
    # 수정할 데이터 필터링 (None이 아닌 값만)
    update_data = {k: v for k, v in kwargs.items() if v is not None}
    
    if not update_data:
        return await get_user_by_id(db, user_id)
    
    # 업데이트 실행
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(**update_data)
    )
    await db.commit()
    
    # 수정된 사용자 조회
    return await get_user_by_id(db, user_id)


async def update_password(
    db: AsyncSession,
    user_id: UUID,
    new_password: str
) -> Optional[User]:
    """
    비밀번호 변경
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        new_password: 새 비밀번호 (평문)
    
    Returns:
        Optional[User]: 수정된 사용자 객체 또는 None
    """
    # 비밀번호 해싱
    hashed_password = hash_password(new_password)
    
    # 업데이트 실행
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(password=hashed_password)
    )
    await db.commit()
    
    return await get_user_by_id(db, user_id)


async def update_last_login(
    db: AsyncSession,
    user_id: UUID
) -> None:
    """
    마지막 로그인 시각 업데이트
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
    """
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(lastLoginAt=datetime.utcnow())
    )
    await db.commit()


async def deactivate_user(
    db: AsyncSession,
    user_id: UUID
) -> Optional[User]:
    """
    사용자 비활성화 (soft delete)
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
    
    Returns:
        Optional[User]: 비활성화된 사용자 객체 또는 None
    """
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(isActive=False)
    )
    await db.commit()
    
    return await get_user_by_id(db, user_id)


async def delete_user(
    db: AsyncSession,
    user_id: UUID
) -> bool:
    """
    사용자 완전 삭제 (hard delete)
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
    
    Returns:
        bool: 삭제 성공 여부
    """
    user = await get_user_by_id(db, user_id)
    if user is None:
        return False
    
    await db.delete(user)
    await db.commit()
    
    return True

