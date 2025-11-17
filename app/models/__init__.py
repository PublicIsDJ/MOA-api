"""
SQLAlchemy 모델 통합
"""
from app.database.connection import Base
from app.models.user import User
from app.models.card import Card
from app.models.user_card_activity import UserCardActivity
from app.models.share import Share
from app.models.notification import Notification
from app.models.refresh_token import RefreshToken

# 모든 모델을 import하여 Alembic이 인식할 수 있도록 함
__all__ = [
    "Base",
    "User",
    "Card",
    "UserCardActivity",
    "Share",
    "Notification",
    "RefreshToken", # 추가
]

