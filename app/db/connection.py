"""
데이터베이스 연결 설정
PostgreSQL + SQLAlchemy 비동기 연결
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# SQLAlchemy Base 클래스 (모든 모델이 상속)
Base = declarative_base()

# 비동기 엔진 생성
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # SQL 쿼리 로그 출력 (개발 환경에서만)
    future=True,
    pool_pre_ping=True,  # 연결 상태 확인
)

# 비동기 세션 팩토리
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# 의존성 주입용 DB 세션 생성 함수
async def get_db() -> AsyncSession:
    """
    FastAPI 의존성 주입용 DB 세션 생성
    
    Usage:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
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


# 테이블 생성 함수 (개발 환경에서만 사용, 프로덕션에서는 Alembic 사용)
async def create_tables():
    """
    모든 테이블 생성 (개발용)
    프로덕션에서는 Alembic 마이그레이션 사용 권장
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# 테이블 삭제 함수 (테스트용)
async def drop_tables():
    """
    모든 테이블 삭제 (테스트용)
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

