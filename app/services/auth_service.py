"""
Auth Service - 인증 관련 비즈니스 로직
"""
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, TokenResponse
from app.services.user import user_service
from app.utils.jwt import create_access_token, create_refresh_token, verify_token
from app.utils.password import verify_password
from app.repositories.refresh_token import refresh_token_repository
import hashlib



class AuthService:
    """인증 비즈니스 로직"""

    async def register(
            self,
            db: AsyncSession,
            user_data: UserCreate
    ) -> User:
        """
        회원가입
        
        비즈니스 로직:
        - userId 중복 체크
        - 사용자 생성 (user_service 위임)
        
        Args:
            db: 데이터베이스 세션
            user_data: 회원가입 요청 데이터
            
        Raises:
            HTTPException: userId 중복 시
        """
        # 1. userId 중복 체크
        existing_user = await user_service.get_user_by_userId(db, user_data.userId)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용중인 아이디입니다."
            )
        
        # 2. 사용자 생성 (비밀번호 해싱은 user_service가 처리)
        new_user = await user_service.create_user(
            db=db,
            userId=user_data.userId,
            password=user_data.password,
            userName=user_data.userName,
            gender=user_data.gender,
            interest=user_data.interest,
            phoneNumber=user_data.phoneNumber,
        )

        return new_user
    
    async def login(
            self,
            db: AsyncSession,
            login_data: UserLogin
    ) -> TokenResponse:
        """
        로그인
        
        비즈니스 로직:
        - 사용자 존재 확인
        - 비밀번호 검증
        - 계정 활성화 확인
        - JWT 토큰 생성 (액세스 + 리프레시)
        - 마지막 로그인 시간 업데이트
        
        Args:
            db: 데이터베이스 세션
            login_data: 로그인 요청 데이터
            
        Returns:
            TokenResponse: JWT 토큰 (accessToken, refreshToken)
            
        Raises:
            HTTPException: 인증 실패 시
        """
        # 1. 사용자 조회
        user = await user_service.get_user_by_userId(db, login_data.userId)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="아이디 또는 비밀번호가 올바르지 않습니다"
            )
        
        # 2. 비밀번호 검증
        if not user.password or not verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="아이디 또는 비밀번호가 올바르지 않습니다"
            )
        
        # 3. 계정 활성화 확인
        if not user.isActive:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="비활성화된 계정입니다"
            )
        
        # 4. 마지막 로그인 시각 업데이트
        await user_service.update_last_login(db, user.id)

        # 5. JWT 토큰 생성
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # 6. 리프레시 토큰 DB 저장 (해시값으로 저장)
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        await refresh_token_repository.create(
            db=db,
            user_id=user.id,
            token=token_hash,
            device_info=None, # TODO: Request에서 User-Agent 추출
            ip_address=None, # TODO: Request에서 IP 추출
        )

        return TokenResponse(
            accessToken=access_token,
            refreshToken=refresh_token,
            tokenType="bearer"
        )
    
    async def refresh_access_token(
            self,
            db: AsyncSession,
            refresh_token: str
    ) -> TokenResponse:
        """
        리프레시 토큰으로 새 액세스 토큰 발급
        
        비즈니스 로직:
        - 리프레시 토큰 검증
        - 사용자 존재 및 활성화 확인
        - 새 액세스 토큰 + 리프레시 토큰 생성
        
        Args:
            db: 데이터베이스 세션
            refresh_token: 리프레시 토큰
            
        Returns:
            TokenResponse: 새로운 JWT 토큰
            
        Raises:
            HTTPException: 토큰 검증 실패 시
        """
        # 1. 리프레시 토큰 검증 및 사용자 ID 추출
        user_id: Optional[UUID] = verify_token(refresh_token, token_type="refresh")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 리프레시 토큰입니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 2. DB에서 리프레시 토큰 확인 (해시값으로 조회)
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        stored_token = await refresh_token_repository.get_by_token(db, token_hash)

        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 리프레시 토큰입니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 3. 토큰 유효성 확인 (폐기/만료 체크)
        if not stored_token.is_valid():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="만료되었거나 폐기된 토큰입니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 4. 사용자 존재 확인
        user = await user_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자를 찾을 수 없습니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 5. 계정 활성화 확인
        if not user.isActive:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="비활성화된 계정입니다"
            )
        
        # 6. 기존 토큰 폐기 (Refresh Token Rotation)
        await refresh_token_repository.revoke_token(db, token_hash)
        
        # 7. 새 토큰 생성
        new_access_token = create_access_token(user.id)
        new_refresh_token = create_refresh_token(user.id)

        # 8. 새 리프레시 토큰 DB 저장
        new_token_hash = hashlib.sha256(new_refresh_token.encode()).hexdigest()
        await refresh_token_repository.create(
            db=db,
            user_id=user.id,
            token=new_token_hash,
            device_info=None,
            ip_address=None,
        )

        return TokenResponse(
            accessToken=new_access_token,
            refreshToken=new_refresh_token,
            tokenType="bearer"
        )
    
    async def logout(
            self,
            db: AsyncSession,
            refresh_token: str
    ) -> bool:
        """
        로그아웃 - 리프레시 토큰 폐기
        
        Args:
            db: 데이터베이스 세션
            refresh_token: 폐기할 리프레시 토큰
            
        Retruns:
            bool: 성공 여부
        """
        # 토큰 해시값으로 변환
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

        # 토큰 폐기
        result = await refresh_token_repository.revoke_token(db, token_hash)

        return result
    

# 싱글톤 인스턴스
auth_service = AuthService()