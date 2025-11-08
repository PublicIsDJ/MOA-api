"""
Auth API 라우터
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse
from app.schemas.common import SuccessResponse
from app.crud import user as user_crud
from app.utils.jwt import create_access_token, create_refresh_token
from app.utils.password import verify_password


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
    # userId 중복 체크
    existing_user = await user_crud.get_user_by_userId(db, user_data.userId)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 아이디입니다"
        )
    
    # 사용자 생성
    new_user = await user_crud.create_user(
        db=db,
        userId=user_data.userId,
        password=user_data.password,
        userName=user_data.userName,
        gender=user_data.gender,
        interest=user_data.interest,
        phoneNumber=user_data.phoneNumber,
    )
    
    return new_user


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
    # 사용자 조회
    user = await user_crud.get_user_by_userId(db, login_data.userId)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다"
        )
    
    # 비밀번호 검증
    if not user.password or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다"
        )
    
    # 비활성 계정 체크
    if not user.isActive:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 계정입니다"
        )
    
    # 마지막 로그인 시각 업데이트
    await user_crud.update_last_login(db, user.id)
    
    # JWT 토큰 생성
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    return TokenResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        tokenType="bearer"
    )


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

