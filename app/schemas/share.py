"""
Share Pydantic 스키마
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


# ==================== 요청 스키마 ====================

class ShareCreate(BaseModel):
    """
    공유 링크 생성 요청
    """
    cardId: UUID = Field(description="공유할 카드 ID")
    password: Optional[str] = Field(default=None, min_length=4, max_length=50, description="비밀번호 (선택)")
    expiryDays: Optional[int] = Field(default=7, ge=1, le=365, description="만료 일수 (1~365일, 기본 7일, null이면 만료 없음)")


class ShareAccessRequest(BaseModel):
    """
    공유 링크 접근 요청 (비밀번호 필요 시)
    """
    password: str = Field(description="공유 링크 비밀번호")


class ShareUpdate(BaseModel):
    """
    공유 링크 수정 요청
    """
    password: Optional[str] = Field(default=None, min_length=4, max_length=50, description="비밀번호")
    expiryDays: Optional[int] = Field(default=None, ge=1, le=365, description="만료 일수 (1~365일, null이면 만료 없음)")
    isActive: Optional[bool] = Field(default=None, description="활성화 여부")


# ==================== 응답 스키마 ====================

class ShareResponse(BaseModel):
    """
    공유 링크 정보 응답
    """
    id: UUID = Field(description="공유 링크 ID")
    userId: UUID = Field(description="공유 생성자 ID")
    cardId: UUID = Field(description="공유할 카드 ID")
    shareToken: str = Field(description="공유 토큰")
    hasPassword: bool = Field(description="비밀번호 설정 여부")
    expiryDate: Optional[datetime] = Field(default=None, description="만료일")
    viewCount: int = Field(description="조회수")
    isActive: bool = Field(description="활성화 여부")
    createdAt: datetime = Field(description="생성 시각")
    updatedAt: datetime = Field(description="수정 시각")

    model_config = {
        "from_attributes": True
    }

    @classmethod
    def from_orm_with_password_check(cls, share):
        """ORM 객체에서 변환하며 hasPassword 필드 추가"""
        data = {
            "id": share.id,
            "userId": share.userId,
            "cardId": share.cardId,
            "shareToken": share.shareToken,
            "hasPassword": share.password is not None,
            "expiryDate": share.expiryDate,
            "viewCount": share.viewCount,
            "isActive": share.isActive,
            "createdAt": share.createdAt,
            "updatedAt": share.updatedAt,
        }
        return cls(**data)


class ShareWithCardResponse(BaseModel):
    """
    공유 링크 + 카드 정보 응답
    """
    id: UUID = Field(description="공유 링크 ID")
    userId: UUID = Field(description="공유 생성자 ID")
    cardId: UUID = Field(description="카드 ID")
    cardTitle: str = Field(description="카드 제목")
    cardThumbnailUrl: Optional[str] = Field(default=None, description="카드 썸네일")
    shareToken: str = Field(description="공유 토큰")
    shareUrl: str = Field(description="공유 URL")
    hasPassword: bool = Field(description="비밀번호 설정 여부")
    expiryDate: Optional[datetime] = Field(default=None, description="만료일")
    viewCount: int = Field(description="조회수")
    isActive: bool = Field(description="활성화 여부")
    createdAt: datetime = Field(description="생성 시각")


class ShareStatsResponse(BaseModel):
    """
    공유 통계 응답
    """
    totalShares: int = Field(description="총 공유 수")
    activeShares: int = Field(description="활성 공유 수")
    totalViews: int = Field(description="총 조회수")
    mostViewedShareId: Optional[UUID] = Field(default=None, description="가장 많이 조회된 공유 ID")

