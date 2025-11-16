"""
애플리케이션 설정
환경변수를 로드하고 관리
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    환경변수 설정 클래스
    .env 파일에서 자동으로 로드
    """
    
    # 환경 설정
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # 데이터베이스 설정
    DATABASE_URL: str
    
    # JWT 보안 설정
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7 # 리프레시 토큰 만료 기간 (7일)
    JWT_EXPIRATION_HOURS: int = 2  # 액세스 토큰 만료 시간 (시간)
    
    # CORS 설정
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # API 설정
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "MOA-API"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """CORS 허용 도메인 리스트로 변환"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 전역 설정 인스턴스
settings = Settings()

