"""
User Pydantic 스키마
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

from app.models.enums import GenderType, InterestType, SocialProviderType


# ==================== 요청 스키마 ====================

class UserCreate(BaseModel):
    """
    회원가입 요청 (일반 로그인)
    """
    userId: str = Field(min_length=4, max_length=255, description="로그인 ID")
    password: str = Field(min_length=8, max_length=100, description="비밀번호 (최소 8자)")
    userName: str = Field(min_length=2, max_length=100, description="사용자 이름")
    gender: Optional[GenderType] = Field(default=None, description="성별")
    interest: Optional[InterestType] = Field(default=None, description="관심사")
    phoneNumber: Optional[str] = Field(default=None, max_length=20, description="전화번호")

    @field_validator('userId')
    @classmethod
    def validate_userId(cls, v: str) -> str:
        """로그인 ID 검증"""
        if len(v) < 4:
            raise ValueError('로그인 ID는 최소 4자 이상이어야 합니다')
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError('로그인 ID는 영문, 숫자, ., _, - 만 사용 가능합니다')
        return v.lower()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """비밀번호 검증: 영문, 숫자, 특수문자 중 2가지 이상 포함"""
        if len(v) < 8:
            raise ValueError('비밀번호는 최소 8자 이상이어야 합니다')

        has_letter = bool(re.search(r'[a-zA-Z]', v))
        has_digit = bool(re.search(r'\d', v))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', v))

        if sum([has_letter, has_digit, has_special]) < 2:
            raise ValueError('비밀번호는 영문, 숫자, 특수문자 중 2가지 이상을 포함해야 합니다')

        return v

    @field_validator('phoneNumber')
    @classmethod
    def validate_phoneNumber(cls, v: Optional[str]) -> Optional[str]:
        """전화번호 검증"""
        if v is None:
            return v

        # 숫자와 하이픈만 허용
        if not re.match(r'^[0-9-]+$', v):
            raise ValueError('전화번호는 숫자와 하이픈(-)만 포함할 수 있습니다')

        return v


class UserLogin(BaseModel):
    """
    로그인 요청
    """
    userId: str = Field(description="로그인 ID")
    password: str = Field(description="비밀번호")


class SocialLoginRequest(BaseModel):
    """
    소셜 로그인 요청
    """
    provider: SocialProviderType = Field(description="소셜 로그인 제공자")
    accessToken: str = Field(description="소셜 로그인 액세스 토큰")


class UserUpdate(BaseModel):
    """
    프로필 수정 요청
    """
    userName: Optional[str] = Field(default=None, min_length=2, max_length=100, description="사용자 이름")
    gender: Optional[GenderType] = Field(default=None, description="성별")
    interest: Optional[InterestType] = Field(default=None, description="관심사")
    phoneNumber: Optional[str] = Field(default=None, max_length=20, description="전화번호")
    profileImageUrl: Optional[str] = Field(default=None, description="프로필 이미지 URL")

    @field_validator('phoneNumber')
    @classmethod
    def validate_phoneNumber(cls, v: Optional[str]) -> Optional[str]:
        """전화번호 검증"""
        if v is None:
            return v

        if not re.match(r'^[0-9-]+$', v):
            raise ValueError('전화번호는 숫자와 하이픈(-)만 포함할 수 있습니다')

        return v


class PasswordChange(BaseModel):
    """
    비밀번호 변경 요청
    """
    currentPassword: str = Field(description="현재 비밀번호")
    newPassword: str = Field(min_length=8, max_length=100, description="새 비밀번호")

    @field_validator('newPassword')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """비밀번호 검증"""
        if len(v) < 8:
            raise ValueError('비밀번호는 최소 8자 이상이어야 합니다')

        has_letter = bool(re.search(r'[a-zA-Z]', v))
        has_digit = bool(re.search(r'\d', v))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', v))

        if sum([has_letter, has_digit, has_special]) < 2:
            raise ValueError('비밀번호는 영문, 숫자, 특수문자 중 2가지 이상을 포함해야 합니다')

        return v


# ==================== 응답 스키마 ====================

class UserResponse(BaseModel):
    """
    사용자 정보 응답
    """
    id: UUID = Field(description="사용자 ID")
    userId: str = Field(description="로그인 ID")
    userName: str = Field(description="사용자 이름")
    gender: Optional[GenderType] = Field(default=None, description="성별")
    interest: Optional[InterestType] = Field(default=None, description="관심사")
    phoneNumber: Optional[str] = Field(default=None, description="전화번호")
    profileImageUrl: Optional[str] = Field(default=None, description="프로필 이미지 URL")
    socialProvider: Optional[SocialProviderType] = Field(default=None, description="소셜 로그인 제공자")
    isActive: bool = Field(description="계정 활성화 여부")
    lastLoginAt: Optional[datetime] = Field(default=None, description="마지막 로그인 시각")
    createdAt: datetime = Field(description="가입 시각")

    model_config = {
        "from_attributes": True  # SQLAlchemy 모델에서 자동 변환
    }


class TokenResponse(BaseModel):
    """
    JWT 토큰 응답
    """
    accessToken: str = Field(description="JWT 액세스 토큰")
    refreshToken: str = Field(description="JWT 리프레시 토큰")
    tokenType: str = Field(default="bearer", description="토큰 타입")


class UserProfileResponse(UserResponse):
    """
    프로필 상세 응답 (통계 포함)
    """
    totalActivities: int = Field(default=0, description="총 활동 수")
    totalShares: int = Field(default=0, description="총 공유 수")

