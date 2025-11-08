"""
데이터베이스 의존성
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    데이터베이스 세션 의존성
    
    FastAPI 의존성으로 사용되며, 요청마다 새로운 DB 세션을 생성하고
    요청 종료 시 자동으로 세션을 닫습니다.
    
    Yields:
        AsyncSession: SQLAlchemy 비동기 세션
    
    Example:
        ```python
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            users = result.scalars().all()
            return users
        ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

