"""
User 모델
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum, CheckConstraint, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database.connection import Base
from app.models.base import TimestampMixin
from app.models.enums import GenderType, InterestType, SocialProviderType


class User(Base, TimestampMixin):
    """
    사용자 계정 정보
    - 일반 로그인 및 소셜 로그인 지원
    """
    __tablename__ = "users"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="사용자 고유 식별자"
    )

    # 로그인 정보
    userId = Column(
        String(255),
        unique=True,
        nullable=False,
        comment="로그인 id"
    )
    password = Column(
        String(255),
        nullable=True,
        comment="비밀번호 (bcrypt 해시, 소셜 로그인 시 NULL)"
    )

    # 프로필 정보
    userName = Column(
        String(100),
        nullable=False,
        comment="사용자 이름"
    )
    gender = Column(
        Enum(GenderType, name="gender_type"),
        nullable=True,
        comment="성별"
    )
    interest = Column(
        Enum(InterestType, name="interest_type"),
        nullable=True,
        comment="관심사"
    )
    phoneNumber = Column(
        String(20),
        nullable=True,
        comment="전화번호"
    )
    profileImageUrl = Column(
        String,
        nullable=True,
        comment="프로필 이미지 URL"
    )

    # 소셜 로그인 정보
    socialProvider = Column(
        Enum(SocialProviderType, name="social_provider_type"),
        nullable=True,
        comment="소셜 로그인 제공자"
    )
    socialId = Column(
        String(255),
        nullable=True,
        comment="소셜 로그인 ID"
    )

    # 계정 상태
    isActive = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        comment="계정 활성화 여부"
    )
    lastLoginAt = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="마지막 로그인 시각"
    )

    # Relationships
    user_card_activities = relationship(
        "UserCardActivity",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    shares = relationship(
        "Share",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("ix_users_userId", "userId", unique=True),
        Index(
            "ix_users_social_login",
            "socialProvider",
            "socialId",
            unique=True,
            postgresql_where=(socialProvider.isnot(None))
        ),
        # CHECK 제약조건: 일반 로그인 OR 소셜 로그인
        CheckConstraint(
            """
            (password IS NOT NULL AND "socialProvider" IS NULL AND "socialId" IS NULL) OR
            (password IS NULL AND "socialProvider" IS NOT NULL AND "socialId" IS NOT NULL)
            """,
            name="chk_social_login"
        ),
    )

    def __repr__(self):
        return f"<User(id={self.id}, userId={self.userId}, userName={self.userName})>"

