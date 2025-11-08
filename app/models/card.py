"""
Card 모델
"""
from sqlalchemy import Column, String, Boolean, Text, Index, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.db.connection import Base
from app.models.base import TimestampMixin


class Card(Base, TimestampMixin):
    """
    카드 마스터 데이터
    - 관리자가 미리 생성한 활동 카드
    - QR 코드로 접근 가능
    """
    __tablename__ = "cards"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="카드 고유 식별자"
    )

    # 카드 기본 정보
    qrCode = Column(
        String(255),
        unique=True,
        nullable=False,
        comment="QR 코드 값"
    )
    title = Column(
        String(255),
        nullable=False,
        comment="카드 제목"
    )
    description = Column(
        Text,
        nullable=True,
        comment="카드 설명"
    )

    # 활동 정보
    activityType = Column(
        String(100),
        nullable=False,
        comment="활동 유형 (season_select, drawing, quiz 등)"
    )
    activityData = Column(
        JSONB,
        nullable=False,
        comment="활동 옵션/설정 JSON"
    )

    # 썸네일
    thumbnailUrl = Column(
        Text,
        nullable=True,
        comment="카드 썸네일 이미지 URL"
    )

    # 활성화 상태
    isActive = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        comment="활성화 여부"
    )

    # Relationships
    user_card_activities = relationship(
        "UserCardActivity",
        back_populates="card",
        cascade="all, delete-orphan"
    )
    shares = relationship(
        "Share",
        back_populates="card",
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("ix_cards_qrCode", "qrCode", unique=True),
        Index("ix_cards_activityType", "activityType"),
        Index("ix_cards_isActive", "isActive"),
    )

    def __repr__(self):
        return f"<Card(id={self.id}, qrCode={self.qrCode}, title={self.title})>"

