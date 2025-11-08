"""
Share 모델
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.connection import Base
from app.models.base import TimestampMixin


class Share(Base, TimestampMixin):
    """
    카드 공유 링크
    - 토큰 기반 공유
    """
    __tablename__ = "shares"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="공유 링크 고유 식별자"
    )

    # Foreign Keys
    userId = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="공유 생성자"
    )
    cardId = Column(
        UUID(as_uuid=True),
        ForeignKey("cards.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="공유할 카드"
    )

    # 공유 정보
    shareToken = Column(
        String(255),
        unique=True,
        nullable=False,
        comment="공유 토큰 (자동 생성)"
    )
    password = Column(
        String(255),
        nullable=True,
        comment="비밀번호 (bcrypt 해시, 선택)"
    )
    expiryDate = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="만료일 (선택)"
    )

    # 통계
    viewCount = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="조회수"
    )

    # 상태
    isActive = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        comment="활성화 여부"
    )

    # Relationships
    user = relationship("User", back_populates="shares")
    card = relationship("Card", back_populates="shares")

    # Indexes
    __table_args__ = (
        Index("ix_shares_shareToken", "shareToken", unique=True),
        Index("ix_shares_userId", "userId"),
        Index("ix_shares_cardId", "cardId"),
        Index("ix_shares_active_expiry", "isActive", "expiryDate"),
        Index("ix_shares_user_active", "userId", "isActive"),
    )

    def __repr__(self):
        return f"<Share(id={self.id}, shareToken={self.shareToken}, cardId={self.cardId})>"

