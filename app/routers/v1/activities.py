"""
Activity API 라우터
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_active_user
from app.schemas.user_card_activity import (
    ActivityCreate,
    ActivityResponse,
    ActivityStatsResponse
)
from app.schemas.common import PaginatedResponse
from app.services.user_card_activity import user_card_activity_service
from app.models.user import User


router = APIRouter(prefix="/activities", tags=["Activity"])


@router.post(
    "",
    response_model=ActivityResponse,
    status_code=201,
    summary="활동 기록 생성",
    description="카드 활동 결과 저장"
)
async def create_activity(
    activity_data: ActivityCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ## 활동 기록 생성
    
    **인증 필요:** Bearer 토큰
    
    **요청 본문:**
    - `cardId`: 카드 ID
    - `activityResult`: 활동 결과 데이터 (JSON)
    
    **응답:**
    - 생성된 활동 기록
    """
    # 활동 기록 생성 (검증 포함)
    activity = await user_card_activity_service.create_activity_with_validation(
        db=db,
        userId=current_user.id,
        cardId=activity_data.cardId,
        activityResult=activity_data.activityResult
    )
    
    return activity


@router.get(
    "/me",
    response_model=PaginatedResponse[ActivityResponse],
    summary="내 활동 목록 조회",
    description="현재 사용자의 활동 기록 목록"
)
async def get_my_activities(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(20, ge=1, le=100, description="조회할 개수"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ## 내 활동 목록 조회
    
    **인증 필요:** Bearer 토큰
    
    **쿼리 파라미터:**
    - `skip`: 건너뛸 개수 (기본: 0)
    - `limit`: 조회할 개수 (기본: 20, 최대: 100)
    
    **응답:**
    - 활동 기록 목록 (최신순)
    """
    # 활동 목록 조회
    activities = await user_card_activity_service.get_user_activities(
        db=db,
        userId=current_user.id,
        skip=skip,
        limit=limit
    )
    
    # 총 개수
    total = await user_card_activity_service.get_user_activities_count(
        db=db,
        userId=current_user.id
    )
    
    return PaginatedResponse(
        items=activities,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{activity_id}",
    response_model=ActivityResponse,
    summary="활동 상세 조회",
    description="특정 활동 기록 상세 조회"
)
async def get_activity(
    activity_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ## 활동 상세 조회
    
    **인증 필요:** Bearer 토큰
    
    **경로 파라미터:**
    - `activity_id`: 활동 기록 ID
    
    **응답:**
    - 활동 기록 상세 정보
    """
    # 활동 조회 (권한 확인 포함)
    activity = await user_card_activity_service.get_activity_with_permission_check(
        db=db,
        activity_id=activity_id,
        userId=current_user.id
    )
    
    return activity


@router.get(
    "/stats/me",
    response_model=ActivityStatsResponse,
    summary="활동 통계 조회",
    description="현재 사용자의 활동 통계"
)
async def get_my_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ## 활동 통계 조회
    
    **인증 필요:** Bearer 토큰
    
    **응답:**
    - 총 활동 수
    - 활동한 카드 수
    - 최근 활동 날짜
    """
    stats = await user_card_activity_service.get_activity_stats(db, current_user.id)
    
    return ActivityStatsResponse(
        totalActivities=stats["totalActivities"],
        uniqueCards=stats["uniqueCards"],
        recentActivityDate=stats["recentActivityDate"]
    )

