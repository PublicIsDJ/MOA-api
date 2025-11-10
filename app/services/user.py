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


# 싱글톤 인스턴스
user_service = UserService()

