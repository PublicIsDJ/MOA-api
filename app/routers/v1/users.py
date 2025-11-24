"""
User API 라우터
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_active_user
from app.schemas.user import UserResponse, UserUpdate, PasswordChange
from app.schemas.common import SuccessResponse
from app.services.user import user_service
from app.models.user import User


router = APIRouter(prefix="/users", tags=["User"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="내 정보 조회",
    description="현재 로그인한 사용자의 정보 조회"
)
async def get_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    ## 내 정보 조회
    
    **인증 필요:** Bearer 토큰
    
    **응답:**
    - 사용자 정보 (비밀번호 제외)
    """
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="내 정보 수정",
    description="사용자 정보 수정 (이름, 성별, 관심사, 전화번호 등)"
)
async def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ## 내 정보 수정
    
    **인증 필요:** Bearer 토큰
    
    **요청 본문:**
    - `userName`: 사용자 이름 (선택)
    - `gender`: 성별 (선택)
    - `interest`: 관심사 (선택)
    - `phoneNumber`: 전화번호 (선택)
    - `profileImageUrl`: 프로필 이미지 URL (선택)
    
    **응답:**
    - 수정된 사용자 정보
    """
    # 사용자 정보 수정
    updated_user = await user_service.update_user_profile(
        db=db,
        user_id=current_user.id,
        userName=user_data.userName,
        gender=user_data.gender,
        interest=user_data.interest,
        phoneNumber=user_data.phoneNumber,
        profileImageUrl=user_data.profileImageUrl,
    )
    
    return updated_user


@router.post(
    "/me/password",
    response_model=SuccessResponse,
    summary="비밀번호 변경",
    description="현재 비밀번호 확인 후 새 비밀번호로 변경"
)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ## 비밀번호 변경
    
    **인증 필요:** Bearer 토큰
    
    **요청 본문:**
    - `currentPassword`: 현재 비밀번호
    - `newPassword`: 새 비밀번호 (8자 이상)
    
    **응답:**
    - 성공 메시지
    """
    await user_service.change_password_with_validation(
        db=db,
        user=current_user,
        current_password=password_data.currentPassword,
        new_password=password_data.newPassword
    )
    
    return SuccessResponse(
        success=True,
        message="비밀번호가 변경되었습니다"
    )


@router.delete(
    "/me",
    response_model=SuccessResponse,
    summary="회원 탈퇴",
    description="계정 비활성화 (soft delete)"
)
async def withdraw(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ## 회원 탈퇴
    
    **인증 필요:** Bearer 토큰
    
    계정을 비활성화합니다 (soft delete).
    데이터는 보관되며, 로그인이 불가능해집니다.
    
    **응답:**
    - 성공 메시지
    """
    # 계정 비활성화
    await user_service.deactivate_user(db, current_user.id)
    
    return SuccessResponse(
        success=True,
        message="회원 탈퇴가 완료되었습니다"
    )

