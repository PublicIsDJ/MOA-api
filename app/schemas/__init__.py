"""
Pydantic 스키마 통합
"""
from app.schemas.common import (
    PaginationParams,
    PaginatedResponse,
    SuccessResponse,
    ErrorResponse,
)
from app.schemas.user import (
    UserCreate,
    UserLogin,
    SocialLoginRequest,
    UserUpdate,
    PasswordChange,
    UserResponse,
    TokenResponse,
    UserProfileResponse,
)
from app.schemas.card import (
    CardCreate,
    CardUpdate,
    CardResponse,
    CardDetailResponse,
    CardListResponse,
)
from app.schemas.user_card_activity import (
    ActivityCreate,
    ActivityResponse,
    ActivityWithCardResponse,
    ActivityStatsResponse,
)
from app.schemas.share import (
    ShareCreate,
    ShareAccessRequest,
    ShareUpdate,
    ShareResponse,
    ShareWithCardResponse,
    ShareStatsResponse,
)

__all__ = [
    # Common
    "PaginationParams",
    "PaginatedResponse",
    "SuccessResponse",
    "ErrorResponse",
    # User
    "UserCreate",
    "UserLogin",
    "SocialLoginRequest",
    "UserUpdate",
    "PasswordChange",
    "UserResponse",
    "TokenResponse",
    "UserProfileResponse",
    # Card
    "CardCreate",
    "CardUpdate",
    "CardResponse",
    "CardDetailResponse",
    "CardListResponse",
    # UserCardActivity
    "ActivityCreate",
    "ActivityResponse",
    "ActivityWithCardResponse",
    "ActivityStatsResponse",
    # Share
    "ShareCreate",
    "ShareAccessRequest",
    "ShareUpdate",
    "ShareResponse",
    "ShareWithCardResponse",
    "ShareStatsResponse",
]

