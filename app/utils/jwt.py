"""
JWT 토큰 유틸리티
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from jose import JWTError, jwt
from pydantic import ValidationError

from app.core.config import settings


def create_access_token(
    user_id: UUID,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    JWT 액세스 토큰 생성
    
    Args:
        user_id: 사용자 ID (UUID)
        expires_delta: 만료 시간 (기본: 2시간)
    
    Returns:
        str: JWT 토큰
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    to_encode = {
        "sub": str(user_id),  # subject: 사용자 ID
        "exp": expire,         # expiration: 만료 시각
        "iat": datetime.utcnow(),  # issued at: 발급 시각
        "type": "access"       # 토큰 타입
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    user_id: UUID,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    JWT 리프레시 토큰 생성
    
    Args:
        user_id: 사용자 ID (UUID)
        expires_delta: 만료 시간 (기본: 7일)
    
    Returns:
        str: JWT 리프레시 토큰
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[UUID]:
    """
    JWT 토큰 검증 및 사용자 ID 추출
    
    Args:
        token: JWT 토큰
        token_type: 토큰 타입 ("access" 또는 "refresh")
    
    Returns:
        Optional[UUID]: 사용자 ID (검증 실패 시 None)
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # 토큰 타입 확인
        if payload.get("type") != token_type:
            return None
        
        # 사용자 ID 추출
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            return None
        
        # UUID로 변환
        user_id = UUID(user_id_str)
        return user_id
        
    except (JWTError, ValidationError, ValueError):
        return None


def decode_token(token: str) -> Optional[dict]:
    """
    JWT 토큰 디코딩 (검증 없이)
    
    Args:
        token: JWT 토큰
    
    Returns:
        Optional[dict]: 토큰 페이로드 (디코딩 실패 시 None)
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_signature": False}
        )
        return payload
    except JWTError:
        return None


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    JWT 토큰 만료 시각 조회
    
    Args:
        token: JWT 토큰
    
    Returns:
        Optional[datetime]: 만료 시각 (조회 실패 시 None)
    """
    payload = decode_token(token)
    if payload is None:
        return None
    
    exp_timestamp = payload.get("exp")
    if exp_timestamp is None:
        return None
    
    return datetime.fromtimestamp(exp_timestamp)


def is_token_expired(token: str) -> bool:
    """
    JWT 토큰 만료 여부 확인
    
    Args:
        token: JWT 토큰
    
    Returns:
        bool: 만료 여부 (True: 만료됨, False: 유효함)
    """
    expiration = get_token_expiration(token)
    if expiration is None:
        return True
    
    return datetime.utcnow() > expiration

