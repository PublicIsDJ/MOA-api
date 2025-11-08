"""
공통 Pydantic 스키마
"""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field


# Generic Type Variable
T = TypeVar('T')


class PaginationParams(BaseModel):
    """
    페이지네이션 파라미터
    """
    page: int = Field(default=1, ge=1, description="페이지 번호 (1부터 시작)")
    page_size: int = Field(default=20, ge=1, le=100, description="페이지당 항목 수 (최대 100)")

    @property
    def offset(self) -> int:
        """SQL OFFSET 계산"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """SQL LIMIT"""
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """
    페이지네이션 응답
    """
    items: list[T] = Field(description="데이터 목록")
    total: int = Field(description="전체 항목 수")
    page: int = Field(description="현재 페이지")
    page_size: int = Field(description="페이지당 항목 수")
    total_pages: int = Field(description="전체 페이지 수")

    @classmethod
    def create(cls, items: list[T], total: int, page: int, page_size: int):
        """페이지네이션 응답 생성"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )


class SuccessResponse(BaseModel):
    """
    성공 응답
    """
    success: bool = Field(default=True, description="성공 여부")
    message: str = Field(description="응답 메시지")
    data: Optional[dict] = Field(default=None, description="추가 데이터")


class ErrorResponse(BaseModel):
    """
    에러 응답
    """
    success: bool = Field(default=False, description="성공 여부")
    error: str = Field(description="에러 코드")
    message: str = Field(description="에러 메시지")
    details: Optional[dict] = Field(default=None, description="에러 상세 정보")

