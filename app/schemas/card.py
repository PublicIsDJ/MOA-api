"""
Card Pydantic 스키마
"""
from datetime import datetime
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field


# ==================== 요청 스키마 ====================

class CardCreate(BaseModel):
    """
    카드 생성 요청 (관리자용)
    """
    qrCode: str = Field(min_length=1, max_length=255, description="QR 코드 값")
    title: str = Field(min_length=1, max_length=255, description="카드 제목")
    description: Optional[str] = Field(default=None, description="카드 설명")
    activityType: str = Field(min_length=1, max_length=100, description="활동 유형")
    activityData: dict[str, Any] = Field(description="활동 옵션/설정 JSON")
    thumbnailUrl: Optional[str] = Field(default=None, description="썸네일 이미지 URL")
    isActive: bool = Field(default=True, description="활성화 여부")


class CardUpdate(BaseModel):
    """
    카드 수정 요청 (관리자용)
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=255, description="카드 제목")
    description: Optional[str] = Field(default=None, description="카드 설명")
    activityType: Optional[str] = Field(default=None, min_length=1, max_length=100, description="활동 유형")
    activityData: Optional[dict[str, Any]] = Field(default=None, description="활동 옵션/설정 JSON")
    thumbnailUrl: Optional[str] = Field(default=None, description="썸네일 이미지 URL")
    isActive: Optional[bool] = Field(default=None, description="활성화 여부")


# ==================== 응답 스키마 ====================

class CardResponse(BaseModel):
    """
    카드 정보 응답
    """
    id: UUID = Field(description="카드 ID")
    qrCode: str = Field(description="QR 코드 값")
    title: str = Field(description="카드 제목")
    description: Optional[str] = Field(default=None, description="카드 설명")
    activityType: str = Field(description="활동 유형")
    activityData: dict[str, Any] = Field(description="활동 옵션/설정 JSON")
    thumbnailUrl: Optional[str] = Field(default=None, description="썸네일 이미지 URL")
    isActive: bool = Field(description="활성화 여부")
    createdAt: datetime = Field(description="생성 시각")
    updatedAt: datetime = Field(description="수정 시각")

    model_config = {
        "from_attributes": True
    }


class CardDetailResponse(CardResponse):
    """
    카드 상세 응답 (통계 포함)
    """
    totalActivities: int = Field(default=0, description="총 활동 수")
    totalShares: int = Field(default=0, description="총 공유 수")


class CardListResponse(BaseModel):
    """
    카드 목록 응답 (간략 정보)
    """
    id: UUID = Field(description="카드 ID")
    title: str = Field(description="카드 제목")
    activityType: str = Field(description="활동 유형")
    thumbnailUrl: Optional[str] = Field(default=None, description="썸네일 이미지 URL")
    isActive: bool = Field(description="활성화 여부")
    createdAt: datetime = Field(description="생성 시각")

    model_config = {
        "from_attributes": True
    }

