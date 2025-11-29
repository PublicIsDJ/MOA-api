"""
Share API 라우터
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_active_user, get_optional_user
from app.schemas.share import (
    ShareCreate,
    ShareResponse,
    ShareAccessRequest,
    ShareUpdate
)
from app.schemas.common import PaginatedResponse
from app.services.share import share_service
from app.models.user import User

router = APIRouter(prefix="/shares", tags=["Share"])


@router.post(
    "",
    response_model=ShareResponse,
    status_code=201,
    summary="공유 링크 생성",
    description="카드 공유 링크 생성"
)
async def create_share(
    share_data: ShareCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ## 공유 링크 생성

    **인증 필요:** Bearer 토큰

    **요청 본문:**
    - `cardId`: 공유할 카드 ID
    - `password`: 비밀번호 (선택)
    - `expiryDate`: 만료일 (선택)

    **응답:**
    - 생성된 공유 링크 
    """
    # 공유 링크 생성 (검증 포함)
    share = await share_service.create_share_with_validation(
        db=db,
        userId=current_user.id,
        cardId=share_data.cardId,
        password=share_data.password,
        expiryDate=share_data.expiryDate
    )

    return ShareResponse.from_orm_with_password_check(share)


@router.get(
    "/me",
    response_model=PaginatedResponse[ShareResponse],
    summary="내 공유 목록 조회",
    description="현재 사용자의 공유 목록"
)
async def get_my_shares(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(20, ge=1, le=100, description="조회할 개수"),
    isActive: Optional[bool] = Query(None, description="활성화 필터"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ## 내 공유 목록 조회
    
    **인증 필요:** Bearer 토큰
    
    **쿼리 파라미터:**
    - `skip`: 건너뛸 개수 (기본: 0)
    - `limit`: 조회할 개수 (기본: 20, 최대: 100)
    - `isActive`: 활성화 필터 (선택)

    **응답:**
    - 공유 목록 (최신순)
    """
    # 공유 목록 조회
    shares = await share_service.get_user_shares(
        db=db,
        userId=current_user.id,
        skip=skip,
        limit=limit,
        isActive=isActive
    )

    # 총 개수
    total = await share_service.get_user_shares_count(
        db=db,
        userId=current_user.id,
        isActive=isActive
    )

    # hasPassword 필드 추가
    share_responses = [ShareResponse.from_orm_with_password_check(share) for share in shares]

    return PaginatedResponse.create(
        items=share_responses,
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        page_size=limit
    )


@router.get(
    "/token/{share_token}",
    response_model=ShareResponse,
    summary="공유 토큰으로 조회",
    description="공유 토큰으로 공유 링크 정보 조회"
)
async def get_share_by_token(
    share_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    ## 공유 토큰으로 조회

    **인증 불필요**

    **경로 파라미터:**
    - `share_token`: 공유 토큰

    **응답:**
    - 공유 링크 정보 (비밀번호 제외)
    """
    # 공유 링크 조회 (검증 포함)
    share = await share_service.get_share_by_token_with_validation(
        db=db,
        shareToken=share_token
    )

    return ShareResponse.from_orm_with_password_check(share)


@router.get(
    "/{share_id}",
    response_model=ShareResponse,
    summary="공유 상세 조회",
    description="공유 링크 상세 조회"
)
async def get_share(
    share_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ## 공유 상세 조회

    **인증 필요:** Bearer 토큰

    **경로 파라미터:**
    - `share_id`: 공유 링크 ID

    **응답:**
    - 공유 링크 상세 정보
    """
    # 공유 조회 (권한 확인 포함)
    share = await share_service.get_share_with_permission_check(
        db=db,
        share_id=share_id,
        userId=current_user.id
    )

    return ShareResponse.from_orm_with_password_check(share)


@router.patch(
    "/{share_id}",
    response_model=ShareResponse,
    summary="공유 링크 수정",
    description="공유 링크 정보 수정"
)
async def update_share(
    share_id: UUID,
    share_data: ShareUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ## 공유 링크 수정

    **인증 필요:** Bearer 토큰

    **경로 파라미터:**
    - `share_id`: 공유 링크 ID

    **요청 본문:**
    - `password`: 비밀번호 (선택)
    - `expiryDate`: 만료일 (선택)
    - `isActive`: 활성화 여부 (선택)

    **응답:**
    - 수정된 공유 링크
    """
    # 공유 수정 (권한 확인 포함)
    updated_share = await share_service.update_share_with_validation(
        db=db,
        share_id=share_id,
        userId=current_user.id,
        password=share_data.password,
        expiryDate=share_data.expiryDate,
        isActive=share_data.isActive
    )

    return ShareResponse.from_orm_with_password_check(updated_share)


@router.delete(
    "/{share_id}",
    status_code=204,
    summary="공유 링크 삭제",
    description="공유 링크 완전 삭제"
)
async def delete_share(
    share_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ## 공유 링크 삭제

    **인증 필요:** Bearer 토큰

    **경로 파라미터:**
    - `share_id`: 공유 링크 ID
    """
    # 공유 삭제 (권한 확인 포함)
    await share_service.delete_share_with_validation(
        db=db,
        share_id=share_id,
        userId=current_user.id
    )