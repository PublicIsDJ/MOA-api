"""
UserCardActivity Pydantic 스키마
"""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field


# ==================== 요청 스키마 ====================

class ActivityCreate(BaseModel):
    """
    활동 기록 생성 요청
    """
    cardId: UUID = Field(description="카드 ID")
    activityResult: dict[str, Any] = Field(description="활동 결과 JSON")


# ==================== 응답 스키마 ====================

class ActivityResponse(BaseModel):
    """
    활동 기록 응답
    """
    id: UUID = Field(description="활동 기록 ID")
    userId: UUID = Field(description="사용자 ID")
    cardId: UUID = Field(description="카드 ID")
    activityResult: dict[str, Any] = Field(description="활동 결과 JSON")
    completedAt: datetime = Field(description="활동 완료 시각")
    createdAt: datetime = Field(description="기록 생성 시각")

    model_config = {
        "from_attributes": True
    }


class ActivityWithCardResponse(BaseModel):
    """
    활동 기록 + 카드 정보 응답
    """
    id: UUID = Field(description="활동 기록 ID")
    userId: UUID = Field(description="사용자 ID")
    cardId: UUID = Field(description="카드 ID")
    cardTitle: str = Field(description="카드 제목")
    cardThumbnailUrl: Optional[str] = Field(default=None, description="카드 썸네일")
    activityType: str = Field(description="활동 유형")
    activityResult: dict[str, Any] = Field(description="활동 결과 JSON")
    completedAt: datetime = Field(description="활동 완료 시각")
    createdAt: datetime = Field(description="기록 생성 시각")


class ActivityStatsResponse(BaseModel):
    """
    활동 통계 응답
    """
    totalActivities: int = Field(description="총 활동 수")
    uniqueCards: int = Field(description="활동한 카드 수")
    recentActivityDate: Optional[datetime] = Field(default=None, description="최근 활동 일시")

