"""
데이터베이스 Enum 타입 정의
"""
import enum


class GenderType(str, enum.Enum):
    """성별 타입"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class InterestType(str, enum.Enum):
    """관심사 타입"""
    MEMORY_IMPROVEMENT = "memory_improvement"  # 기억력 향상
    CONCENTRATION_TRAINING = "concentration_training"  # 집중력 훈련
    LANGUAGE_ABILITY = "language_ability"  # 언어 능력
    MATH_ABILITY = "math_ability"  # 수리 능력


class SocialProviderType(str, enum.Enum):
    """소셜 로그인 제공자"""
    KAKAO = "kakao"

