"""
RefreshToken Repository
"""
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.core.config import settings


class RefreshTokenRepository:
    """리프레시 토큰 DB 작업"""

    async def create(
            self,
            db: AsyncSession,
            user_id: UUID,
            token: str,
            device_info: Optional[str] = None,
            ip_address: Optional[str] = None,
    ) -> RefreshToken:
        """
        리프레시 토큰 생성
        """
        expires_at = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

        refresh_token = RefreshToken(
            userId = user_id,
            token=token,
            expiresAt = expires_at,
            deviceInfo=device_info,
            ipAddress=ip_address,
        )

        db.add(refresh_token)
        await db.commit()
        await db.refresh(refresh_token)

        return refresh_token
    
    async def get_by_token(
            self,
            db: AsyncSession,
            token: str
    ) -> Optional[RefreshToken]:
        """
        토큰으로 조회
        """
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()
    
    async def revoke_token(
            self,
            db: AsyncSession,
            token: str
    ) -> bool:
        """
        토큰 폐기
        """
        refresh_token = await self.get_by_token(db, token)

        if not refresh_token:
            return False
        
        refresh_token.isRevoked = True
        refresh_token.revokedAt = datetime.utcnow()

        await db.commit()
        return True
    
    async def revoke_all_user_tokens(
            self,
            db: AsyncSession,
            user_id: UUID
    ) -> int:
        """사용자의 모든 토큰 폐기 (로그아웃 all devices)
        """
        result = await db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.userId == user_id,
                    RefreshToken.isRevoked == False
                )
            )
        )
        tokens = result.scalars().all()

        count = 0
        for token in tokens:
            token.isRevoked = True
            token.revokedAt = datetime.utcnow()
            count += 1

        await db.commit()
        return count
    
    async def cleanup_expired_tokes(self, db: AsyncSession) -> int:
        """
        만료된 토큰 삭제 (정리 작업)
        """
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.expiresAt < datetime.utcnow()
            )
        )
        expired_tokens = result.scalars().all()

        for token in expired_tokens:
            await db.delete(token)

        await db.commit()
        return len(expired_tokens)
    

# 싱글톤 인스턴스
refresh_token_repository = RefreshTokenRepository()
