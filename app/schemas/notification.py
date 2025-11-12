"""
Notification Pydantic 스키마
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

# ==================== 요청 스키마 ====================

class NotificationCreate(BaseModel):
    """
    알림 생성 요청 (시스템/관리자용)
    """
    userId: UUID = Field(description="수신자 사용자 ID")
    type: str = Field(min_length=1, max_length=50, description="알림 타입 (Share_received, card_reminder 등)")
    title: str = Field(min_length=1, max_length=255, description="알림 제목")
    message: str = Field(min_length=1, description="알림 내용")
    linkUrl: Optional[str] = Field(default=None, description="링크 URL (선택)")


class NotificationUpdate(BaseModel):
    """
    알림 수정 요청
    """
    isRead: bool = Field(description="읽음 여부")


class NotificationMarkAllAsRead(BaseModel):
    """
    모든 알림 읽음 처리 요청
    """
    pass


# ==================== 응답 스키마 ====================

class NotificationResponse(BaseModel):
    """
    알림 정보 응답
    """
    id: UUID = Field(description="알림 ID")
    userId: UUID = Field(description="수신자 사용자 ID")
    type: str = Field(description="알림 타입")
    title: str = Field(description="알림 제목")
    message: str = Field(description="알림 내용")
    linkUrl: Optional[str] = Field(default=None, description="링크 URL")
    isRead: bool = Field(description="읽음 여부")
    createdAt: datetime = Field(description="생성 시각")

    model_config = {
        "from_attributes": True
    }


class NotificationListResponse(BaseModel):
    """
    알림 목록 응답 (페이지네이션)
    """
    notifications: list[NotificationResponse] = Field(description="알림 목록")
    total: int = Field(description="전체 알림 수")
    unreadCount: int = Field(description="읽지 않은 알림 수")


class NotificationStatsResponse(BaseModel):
    """
    알림 통계 응답
    """
    totalNotifications: int = Field(description="총 알림 수")
    unreadNotifications: int = Field(description="읽지 않은 알림 수")
    readNotifications: int = Field(description="읽은 알림 수")