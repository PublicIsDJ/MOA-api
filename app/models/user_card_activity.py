"""
UserCardActivity 모델
"""
from sqlalchemy import Column, DateTime, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database.connection import Base


class UserCardActivity(Base):
    """
    사용자별 카드 활동 기록
    - 누가, 언제, 어떤 카드에서, 무엇을 선택/입력했는지
    """
    __tablename__ = "user_card_activities"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="활동 기록 고유 식별자"
    )

    # Foreign Keys
    userId = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="활동 수행 사용자"
    )
    cardId = Column(
        UUID(as_uuid=True),
        ForeignKey("cards.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="활동한 카드"
    )

    # 활동 결과
    activityResult = Column(
        JSONB,
        nullable=False,
        comment="사용자 활동 결과 JSON"
    )

    # 시간 정보
    completedAt = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="활동 완료 시각"
    )
    createdAt = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="기록 생성 시각"
    )

    # Relationships
    user = relationship("User", back_populates="user_card_activities")
    card = relationship("Card", back_populates="user_card_activities")

    # Indexes
    __table_args__ = (
        Index("ix_user_card_activities_userId", "userId"),
        Index("ix_user_card_activities_cardId", "cardId"),
        Index("ix_user_card_activities_user_card", "userId", "cardId"),
        Index("ix_user_card_activities_user_completed", "userId", "completedAt"),
        Index("ix_user_card_activities_completedAt", "completedAt"),
    )

    def __repr__(self):
        return f"<UserCardActivity(id={self.id}, userId={self.userId}, cardId={self.cardId})>"

