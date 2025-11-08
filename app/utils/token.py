"""
토큰 생성 유틸리티
"""
import secrets
import string
from typing import Optional


def generate_random_string(
    length: int = 32,
    include_uppercase: bool = True,
    include_lowercase: bool = True,
    include_digits: bool = True,
    include_special: bool = False
) -> str:
    """
    랜덤 문자열 생성
    
    Args:
        length: 문자열 길이 (기본: 32)
        include_uppercase: 대문자 포함 여부
        include_lowercase: 소문자 포함 여부
        include_digits: 숫자 포함 여부
        include_special: 특수문자 포함 여부
    
    Returns:
        str: 랜덤 문자열
    
    Example:
        >>> token = generate_random_string(16)
        >>> len(token)
        16
    """
    characters = ""
    
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_lowercase:
        characters += string.ascii_lowercase
    if include_digits:
        characters += string.digits
    if include_special:
        characters += string.punctuation
    
    if not characters:
        raise ValueError("최소 하나의 문자 타입을 포함해야 합니다")
    
    return ''.join(secrets.choice(characters) for _ in range(length))


def generate_share_token(length: int = 16) -> str:
    """
    공유 링크 토큰 생성
    (URL-safe한 영문 대소문자 + 숫자)
    
    Args:
        length: 토큰 길이 (기본: 16)
    
    Returns:
        str: 공유 토큰
    
    Example:
        >>> token = generate_share_token()
        >>> len(token)
        16
        >>> token = generate_share_token(32)
        >>> len(token)
        32
    """
    return generate_random_string(
        length=length,
        include_uppercase=True,
        include_lowercase=True,
        include_digits=True,
        include_special=False
    )


def generate_verification_code(length: int = 6) -> str:
    """
    인증 코드 생성 (숫자만)
    
    Args:
        length: 코드 길이 (기본: 6)
    
    Returns:
        str: 인증 코드
    
    Example:
        >>> code = generate_verification_code()
        >>> len(code)
        6
        >>> code.isdigit()
        True
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def generate_api_key(prefix: Optional[str] = None, length: int = 32) -> str:
    """
    API 키 생성
    
    Args:
        prefix: API 키 접두사 (예: "moa_")
        length: 랜덤 부분 길이 (기본: 32)
    
    Returns:
        str: API 키
    
    Example:
        >>> api_key = generate_api_key("moa_")
        >>> api_key.startswith("moa_")
        True
    """
    random_part = generate_random_string(
        length=length,
        include_uppercase=True,
        include_lowercase=True,
        include_digits=True,
        include_special=False
    )
    
    if prefix:
        return f"{prefix}{random_part}"
    return random_part


def generate_secure_token(length: int = 64) -> str:
    """
    보안 토큰 생성 (URL-safe base64)
    
    Args:
        length: 토큰 길이 (기본: 64)
    
    Returns:
        str: 보안 토큰
    
    Example:
        >>> token = generate_secure_token()
        >>> len(token)
        64
    """
    return secrets.token_urlsafe(length)[:length]

