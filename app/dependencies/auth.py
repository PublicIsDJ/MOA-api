"""
인증 의존성
"""
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.user import User
from app.utils.jwt import verify_token


# HTTP Bearer 토큰 스키마
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    현재 로그인한 사용자 조회
    
    JWT 토큰을 검증하고 사용자 정보를 반환합니다.
    
    Args:
        credentials: HTTP Authorization 헤더의 Bearer 토큰
        db: 데이터베이스 세션
    
    Returns:
        User: 현재 로그인한 사용자 객체
    
    Raises:
        HTTPException: 인증 실패 시 401 에러
    
    Example:
        ```python
        @router.get("/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user
        ```
    """
    # 토큰 추출
    token = credentials.credentials
    
    # 토큰 검증 및 사용자 ID 추출
    user_id: Optional[UUID] = verify_token(token, token_type="access")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 사용자 조회
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    현재 로그인한 활성 사용자 조회
    
    비활성화된 사용자는 접근을 차단합니다.
    
    Args:
        current_user: 현재 로그인한 사용자
    
    Returns:
        User: 활성 사용자 객체
    
    Raises:
        HTTPException: 비활성 사용자일 경우 403 에러
    
    Example:
        ```python
        @router.post("/cards")
        async def create_card(
            current_user: User = Depends(get_current_active_user)
        ):
            # 활성 사용자만 카드 생성 가능
            ...
        ```
    """
    if not current_user.isActive:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 계정입니다"
        )
    
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    선택적 사용자 인증
    
    토큰이 있으면 사용자를 반환하고, 없으면 None을 반환합니다.
    비로그인 사용자도 접근 가능한 엔드포인트에서 사용합니다.
    
    Args:
        credentials: HTTP Authorization 헤더의 Bearer 토큰 (선택)
        db: 데이터베이스 세션
    
    Returns:
        Optional[User]: 로그인한 사용자 또는 None
    
    Example:
        ```python
        @router.get("/cards/{card_id}")
        async def get_card(
            card_id: UUID,
            current_user: Optional[User] = Depends(get_optional_user)
        ):
            # 로그인 여부와 관계없이 카드 조회 가능
            # 로그인한 경우 추가 정보 제공
            if current_user:
                # 로그인 사용자용 추가 정보
                ...
            else:
                # 비로그인 사용자용 기본 정보
                ...
        ```
    """
    # 토큰이 없으면 None 반환
    if credentials is None:
        return None
    
    # 토큰 추출
    token = credentials.credentials
    
    # 토큰 검증 및 사용자 ID 추출
    user_id: Optional[UUID] = verify_token(token, token_type="access")
    
    if user_id is None:
        return None
    
    # 사용자 조회
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    return user

