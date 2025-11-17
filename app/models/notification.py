"""
Notification 모델
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.connection import Base
from app.models.base import TimestampMixin


class Notification(Base, TimestampMixin):
    """
    사용자 알림
    - 시스템 알림, 공유 알림, 카드 리마인더 등
    """
    __tablename__ = "notifications"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="알림 고유 식별자"
    )

    # Foreign Key
    userId = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="수신자 사용자 ID"
    )

    # 알림 정보
    type = Column(
        String(50),
        nullable=False,
        comment="알림 타입 (share_received, card_reminder 등)"
    )
    title = Column(
        String(255),
        nullable=False,
        comment="알림 제목"
    )
    message = Column(
        String,
        nullable=False,
        comment="알림 내용"
    )
    linkUrl = Column(
        String,
        nullable=True,
        comment="링크 URL (선택)"
    )

    # 상태
    isRead = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="읽음 여부"
    )

    # Relationships
    user = relationship("User", back_populates="notifications")

    # Indexes
    __table_args__ = (
        Index("ix_notifications_userId", "userId"),
        Index("ix_notifications_userId_isRead", "userId", "isRead"),
        Index("ix_notifications_createdAt", "createdAt"),
    )

    def __repr__(self):
        return f"<Notification(id={self.id}, userId={self.userId}, type={self.type}, isRead={self.isRead})>"
