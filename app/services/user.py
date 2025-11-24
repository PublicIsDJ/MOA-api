"""
User Service - 비즈니스 로직
"""
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.enums import SocialProviderType
from app.repositories.user import UserRepository
from app.utils.password import hash_password


class UserService:
    """사용자 비즈니스 로직"""
    
    def __init__(self):
        self.repo = UserRepository()
    
    async def create_user(
        self,
        db: AsyncSession,
        userId: str,
        password: str,
        userName: str,
        gender: Optional[str] = None,
        interest: Optional[str] = None,
        phoneNumber: Optional[str] = None,
    ) -> User:
        """
        일반 회원가입으로 사용자 생성
        
        비즈니스 로직:
        - 비밀번호 해싱
        - 사용자 객체 생성
        """
        hashed_password = hash_password(password)
        
        user = User(
            userId=userId,
            password=hashed_password,
            userName=userName,
            gender=gender,
            interest=interest,
            phoneNumber=phoneNumber,
            isActive=True,
        )
        
        return await self.repo.create(db, user)
    
    async def create_social_user(
        self,
        db: AsyncSession,
        userId: str,
        userName: str,
        socialProvider: SocialProviderType,
        socialId: str,
        gender: Optional[str] = None,
        interest: Optional[str] = None,
        phoneNumber: Optional[str] = None,
        profileImageUrl: Optional[str] = None,
    ) -> User:
        """
        소셜 로그인으로 사용자 생성
        
        비즈니스 로직:
        - 소셜 사용자는 비밀번호 없음
        - 프로필 이미지 URL 저장
        """
        user = User(
            userId=userId,
            password=None,
            userName=userName,
            socialProvider=socialProvider,
            socialId=socialId,
            gender=gender,
            interest=interest,
            phoneNumber=phoneNumber,
            profileImageUrl=profileImageUrl,
            isActive=True,
        )
        
        return await self.repo.create(db, user)
    
    async def get_user_by_id(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        """ID로 사용자 조회"""
        return await self.repo.get_by_id(db, user_id)
    
    async def get_user_by_userId(self, db: AsyncSession, userId: str) -> Optional[User]:
        """userId로 사용자 조회"""
        return await self.repo.get_by_userId(db, userId)
    
    async def get_user_by_social(
        self,
        db: AsyncSession,
        socialProvider: SocialProviderType,
        socialId: str
    ) -> Optional[User]:
        """소셜 로그인 정보로 사용자 조회"""
        return await self.repo.get_by_social(db, socialProvider, socialId)
    
    async def update_user(
        self,
        db: AsyncSession,
        user_id: UUID,
        **kwargs
    ) -> Optional[User]:
        """사용자 정보 수정"""
        return await self.repo.update(db, user_id, **kwargs)
    
    async def update_password(
        self,
        db: AsyncSession,
        user_id: UUID,
        new_password: str
    ) -> Optional[User]:
        """
        비밀번호 변경
        
        비즈니스 로직:
        - 새 비밀번호 해싱
        """
        hashed_password = hash_password(new_password)
        return await self.repo.update_password(db, user_id, hashed_password)
    
    async def update_last_login(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> None:
        """마지막 로그인 시각 업데이트"""
        await self.repo.update_last_login(db, user_id)
    
    async def deactivate_user(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> Optional[User]:
        """사용자 비활성화 (soft delete)"""
        return await self.repo.deactivate(db, user_id)
    
    async def delete_user(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> bool:
        """사용자 완전 삭제 (hard delete)"""
        return await self.repo.delete(db, user_id)
    
    async def update_user_profile(
        self,
        db: AsyncSession,
        user_id: UUID,
        userName: Optional[str] = None,
        gender: Optional[str] = None,
        interest: Optional[str] = None,
        phoneNumber: Optional[str] = None,
        profileImageUrl: Optional[str] = None,
    ) -> User:
        """
        사용자 프로필 수정 (검증 포함)
        
        Raises:
            HTTPException: 사용자를 찾을 수 없는 경우
        """
        from fastapi import HTTPException, status

        #업데이트할 데이터만 필터링
        update_data = {}

        if userName is not None:
            update_data['userName'] = userName
        if gender is not None:
            update_data['gender'] = gender
        if interest is not None:
            update_data['interest'] = interest
        if phoneNumber is not None:
            update_data['phoneNumber'] = phoneNumber
        if profileImageUrl is not None:
            update_data['profileImageUrl'] = profileImageUrl

        updated_user = await self.repo.update(db, user_id, **update_data)

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
            )
        
        return updated_user
    
    async def change_password_with_validation(
        self,
        db: AsyncSession,
        user: User,
        current_password: str,
        new_password: str
    ) -> None:
        """
        비밀번호 변경 (검증 포함)
        
        비즈니스 로직:
        - 소셜 로그인 사용자 체크
        - 현재 비밀번호 확인
        - 새 비밀번호 해싱 및 저장
        
        Raises:
            HTTPException: 검증 실패 시
        """
        from fastapi import HTTPException, status
        from app.utils.password import verify_password

        # 소셜 로그인 사용자는 비밀번호 변경 불가
        if user.socialProvider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="소셜 로그인 사용자는 비밀번호를 변경할 수 없습니다"
            )
        
        # 현재 비밀번호 확인
        if not user.password or not verify_password(current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="현재 비밀번호가 올바르지 않습니다"
            )
        
        # 새 비밀번호로 변경
        await self.update_password(db, user.id, new_password)

    async def deactivate_user_with_validation(
        self,
        db: AsyncSession,
        user: User,
        password: str
    ) -> None:
        """
        계정 비활성화 (검증 포함)
        
        비즈니스 로직:
        - 소셜 로그인 사용자는 비밀번호 없이 탈퇴 가능
        - 일반 사용자는 비밀번호 확인 필요
        
        Raises:
            HTTPException: 비밀번호 불일치 시
        """
        from fastapi import HTTPException, status
        from app.utils.password import verify_password

        # 일반 로그인 사용자는 비밀번호 확인 필요
        if not user.socialProvider:
            if not user.password or not verify_password(password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="비밀번호가 일치하지 않습니다"
                )
            
        # 계정 비활성화
        await self.repo.deactivate(db, user.id)


# 싱글톤 인스턴스
user_service = UserService()

