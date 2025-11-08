"""
API v1 라우터 통합
"""
from fastapi import APIRouter

from app.api.v1 import auth, users, cards, activities, archive


# API v1 라우터
api_router = APIRouter()

# 각 라우터 등록
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(cards.router)
api_router.include_router(activities.router)
api_router.include_router(archive.router)

