"""
Card API 라우터
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_optional_user
from app.schemas.card import CardResponse, CardListResponse
from app.schemas.common import PaginatedResponse
from app.services.card import card_service
from app.models.user import User


router = APIRouter(prefix="/cards", tags=["Card"])


@router.get(
    "",
    response_model=PaginatedResponse[CardListResponse],
    summary="카드 목록 조회",
    description="활성화된 카드 목록 조회 (페이지네이션)"
)
async def get_cards(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(20, ge=1, le=100, description="조회할 개수"),
    activityType: Optional[str] = Query(None, description="활동 타입 필터"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    ## 카드 목록 조회
    
    **인증:** 선택 (비로그인 사용자도 조회 가능)
    
    **쿼리 파라미터:**
    - `skip`: 건너뛸 개수 (기본: 0)
    - `limit`: 조회할 개수 (기본: 20, 최대: 100)
    - `activityType`: 활동 타입 필터 (선택)
    
    **응답:**
    - 카드 목록 (활성화된 카드만)
    """
    # 활성화된 카드만 조회
    cards = await card_service.get_active_cards(
        db=db,
        skip=skip,
        limit=limit,
        activityType=activityType
    )
    
    # 총 개수
    total = await card_service.get_cards_count(
        db=db,
        activityType=activityType,
        isActive=True
    )
    
    # CardListResponse로 변환
    items = [
        CardListResponse(
            id=card.id,
            title=card.title,
            activityType=card.activityType,
            thumbnailUrl=card.thumbnailUrl,
            isActive=card.isActive,
            createdAt=card.createdAt
        )
        for card in cards
    ]
    
    return PaginatedResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{card_id}",
    response_model=CardResponse,
    summary="카드 상세 조회",
    description="카드 상세 정보 조회"
)
async def get_card(
    card_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    ## 카드 상세 조회
    
    **인증:** 선택 (비로그인 사용자도 조회 가능)
    
    **경로 파라미터:**
    - `card_id`: 카드 ID (UUID)
    
    **응답:**
    - 카드 상세 정보
    """
    card = await card_service.get_card_by_id(db, card_id)
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="카드를 찾을 수 없습니다"
        )
    
    # 비활성 카드는 조회 불가
    if not card.isActive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="카드를 찾을 수 없습니다"
        )
    
    return card


@router.post(
    "/scan",
    response_model=CardResponse,
    summary="QR 코드 스캔",
    description="QR 코드로 카드 조회"
)
async def scan_qr_code(
    qrCode: str = Query(..., description="QR 코드"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    ## QR 코드 스캔
    
    **인증:** 선택 (비로그인 사용자도 스캔 가능)
    
    **쿼리 파라미터:**
    - `qrCode`: QR 코드 문자열
    
    **응답:**
    - 카드 정보
    """
    card = await card_service.get_card_by_qr_code(db, qrCode)
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="유효하지 않은 QR 코드입니다"
        )
    
    # 비활성 카드는 조회 불가
    if not card.isActive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="유효하지 않은 QR 코드입니다"
        )
    
    return card

