"""
Archive API 라우터 (보관함)
"""
from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_active_user
from app.crud import user_card_activity as activity_crud
from app.models.user import User


router = APIRouter(prefix="/archive", tags=["Archive"])


@router.get(
    "/cards",
    response_model=List[Dict[str, Any]],
    summary="내가 활동한 카드 목록",
    description="사용자가 활동한 카드 목록 조회 (중복 제거)"
)
async def get_my_completed_cards(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(20, ge=1, le=100, description="조회할 개수"),
    activityType: Optional[str] = Query(None, description="활동 타입 필터"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ## 내가 활동한 카드 목록
    
    **인증 필요:** Bearer 토큰
    
    **쿼리 파라미터:**
    - `skip`: 건너뛸 개수 (기본: 0)
    - `limit`: 조회할 개수 (기본: 20, 최대: 100)
    - `activityType`: 활동 타입 필터 (선택)
    
    **응답:**
    - 카드 정보 + 마지막 활동 시각 + 활동 횟수
    """
    completed_cards = await activity_crud.get_user_completed_cards(
        db=db,
        userId=current_user.id,
        skip=skip,
        limit=limit,
        activityType=activityType
    )
    
    return completed_cards


@router.get(
    "/recent",
    response_model=List[Dict[str, Any]],
    summary="최근 활동 카드",
    description="최근 30일 이내 활동한 카드"
)
async def get_recent_cards(
    days: int = Query(30, ge=1, le=365, description="조회할 일수"),
    limit: int = Query(20, ge=1, le=100, description="조회할 개수"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ## 최근 활동 카드
    
    **인증 필요:** Bearer 토큰
    
    **쿼리 파라미터:**
    - `days`: 조회할 일수 (기본: 30, 최대: 365)
    - `limit`: 조회할 개수 (기본: 20, 최대: 100)
    
    **응답:**
    - 최근 활동 기록 목록
    """
    recent_activities = await activity_crud.get_recent_activities(
        db=db,
        userId=current_user.id,
        days=days,
        limit=limit
    )
    
    return recent_activities


@router.get(
    "/cards/{card_id}/activities",
    response_model=List[Dict[str, Any]],
    summary="카드별 활동 기록 조회",
    description="특정 카드에 대한 내 활동 기록 전체"
)
async def get_card_activities(
    card_id: UUID,
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(20, ge=1, le=100, description="조회할 개수"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ## 카드별 활동 기록 조회
    
    **인증 필요:** Bearer 토큰
    
    **경로 파라미터:**
    - `card_id`: 카드 ID
    
    **쿼리 파라미터:**
    - `skip`: 건너뛸 개수 (기본: 0)
    - `limit`: 조회할 개수 (기본: 20, 최대: 100)
    
    **응답:**
    - 특정 카드에 대한 활동 기록 목록
    """
    activities = await activity_crud.get_user_activities_by_card(
        db=db,
        userId=current_user.id,
        cardId=card_id,
        skip=skip,
        limit=limit
    )
    
    return activities

