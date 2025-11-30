"""
RefreshToken 모델
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.connection import Base
from app.models.base import TimestampMixin


class RefreshToken(Base, TimestampMixin):
    """
    리프레시 토큰 저장소
    - 토큰 무효화 및 로그아웃 관리
    - 멀티 디바이스 로그인 추적
    """
    __tablename__ = "refresh_tokens"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="리프레시 토큰 고유 식별자"
    )

    # Foreign Key
    userId = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="사용자 ID"
    )

    # 토큰 정보
    token = Column(
        String(512),
        unique=True,
        nullable=False,
        comment="리프레시 토큰 (해시값 저장)"
    )
    expiresAt = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="토큰 만료 시각"
    )

    # 디바이스 정보 (선택적)
    deviceInfo = Column(
        String(255),
        nullable=True,
        comment="디바이스 정보 (User-Agent 등)"
    )
    ipAddress = Column(
        String(45),
        nullable=True,
        comment="발급 시 IP 주소"
    )

    # 토큰 상태
    isRevoked = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="토큰 폐기 여부"
    )
    revokedAt = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="폐기된 시각"
    )

    # Relationships
    user = relationship("User", backref="refresh_tokens")

    # Indexes
    __table_args__ = (
        Index("ix_refresh_tokens_userId", "userId"),
        Index("ix_refresh_tokens_token", "token", unique=True),
        Index("ix_refresh_tokens_expiresAt", "expiresAt"),
    )

    def is_expired(self) -> bool:
        """토큰이 만료되었는지 확인"""
        return datetime.now(self.expiresAt.tzinfo) > self.expiresAt
    
    def is_valid(self) -> bool:
        """토큰이 유효한지 확인 (만료되지 않고, 폐기되지 않음)"""
        return not self.isRevoked and not self.is_expired()
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, userId={self.userId}, isRevoked={self.isRevoked})>"
    