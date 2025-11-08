"""
공통 모델 Base 및 Mixin
"""
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func


class TimestampMixin:
    """
    생성/수정 시각 자동 관리 Mixin
    """
    createdAt = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="생성 시각"
    )
    updatedAt = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="수정 시각"
    )

