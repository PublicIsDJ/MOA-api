"""
Auth API 라우터
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse, TokenRefreshRequest
from app.schemas.common import SuccessResponse
from app.services.auth_service import auth_service


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="일반 회원가입 (userId + 비밀번호)"
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    ## 회원가입
    
    **요청 본문:**
    - `userId`: 로그인 ID (4자 이상, 영문/숫자/._- 허용)
    - `password`: 비밀번호 (8자 이상)
    - `userName`: 사용자 이름 (2자 이상)
    - `gender`: 성별 (선택)
    - `interest`: 관심사 (선택)
    - `phoneNumber`: 전화번호 (선택)
    
    **응답:**
    - 생성된 사용자 정보
    """
    return await auth_service.register(db, user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="로그인",
    description="userId + 비밀번호로 로그인"
)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    ## 로그인
    
    **요청 본문:**
    - `userId`: 로그인 ID
    - `password`: 비밀번호
    
    **응답:**
    - `accessToken`: JWT 액세스 토큰
    - `tokenType`: "bearer"
    """
    return await auth_service.login(db, login_data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="토큰 갱신",
    description="리프레시 토큰으로 새 액세스 토큰 발급"
)
async def refresh_token(
    token_data: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    ## 토큰 갱신

    **요청 본문:**
    - `refreshToken`: 리프레시 토큰

    **응답:**
    - `accessToken`: 새로운 JWT 액세스 토큰
    - `refreshToken`: 새로운 JWT 리프레시 토큰
    - `tokenType`: "bearer"
    """
    return await auth_service.refresh_access_token(db, token_data.refreshToken)


@router.post(
    "/logout",
    response_model=SuccessResponse,
    summary="로그아웃",
    description="로그아웃 (클라이언트에서 토큰 삭제)"
)
async def logout():
    """
    ## 로그아웃
    
    JWT는 stateless이므로 서버에서 별도 처리 없음.
    클라이언트에서 토큰을 삭제하면 됩니다.
    """
    return SuccessResponse(
        success=True,
        message="로그아웃되었습니다"
    )

