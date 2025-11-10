"""
Base Repository
"""
from typing import Generic, TypeVar, Type, Optional, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    기본 Repository 클래스
    
    모든 Repository의 공통 CRUD 메서드 제공
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[ModelType]:
        """ID로 조회"""
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """목록 조회"""
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(self, db: AsyncSession, obj_in: ModelType) -> ModelType:
        """생성"""
        db.add(obj_in)
        await db.commit()
        await db.refresh(obj_in)
        return obj_in
    
    async def delete(self, db: AsyncSession, id: UUID) -> bool:
        """삭제"""
        obj = await self.get(db, id)
        if obj is None:
            return False
        
        await db.delete(obj)
        await db.commit()
        return True

