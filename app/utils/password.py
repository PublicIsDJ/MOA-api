"""
비밀번호 해싱 및 검증 유틸리티
"""
from passlib.context import CryptContext


# bcrypt 컨텍스트 생성
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    비밀번호 해싱 (bcrypt)
    
    Args:
        password: 평문 비밀번호
    
    Returns:
        str: 해싱된 비밀번호
    
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> print(hashed)
        $2b$12$...
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    비밀번호 검증
    
    Args:
        plain_password: 평문 비밀번호
        hashed_password: 해싱된 비밀번호
    
    Returns:
        bool: 일치 여부 (True: 일치, False: 불일치)
    
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


def needs_rehash(hashed_password: str) -> bool:
    """
    비밀번호 재해싱 필요 여부 확인
    (bcrypt 라운드 수 변경 등으로 인한 재해싱 필요 시)
    
    Args:
        hashed_password: 해싱된 비밀번호
    
    Returns:
        bool: 재해싱 필요 여부
    """
    return pwd_context.needs_update(hashed_password)

