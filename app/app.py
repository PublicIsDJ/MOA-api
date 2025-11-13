"""
FastAPI 애플리케이션 팩토리
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.v1 import api_router


def create_app() -> FastAPI:
    """
    FastAPI 애플리케이션 생성
    
    Returns:
        FastAPI: 설정된 FastAPI 애플리케이션 인스턴스
    """
    # FastAPI 앱 생성
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="MOA (Memory of Activities) - 뇌 건강 활동 기록 API",
        version="1.0.1",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # API v1 라우터 등록
    app.include_router(api_router, prefix="/api")
    
    # 헬스 체크
    @app.get("/", tags=["Health"])
    def health_check():
        """헬스 체크 엔드포인트"""
        return {
            "status": "ok",
            "message": "MOA API is running",
            "version": "1.0.1"
        }
    
    return app

