import math
from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T] = Field(..., description="List of items for the current page")
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, description="Items per page")
    total: int = Field(..., ge=0, description="Total matching items count")
    total_pages: int = Field(..., ge=0, description="Total number of pages")

    @classmethod
    def create(cls, items: List[T], page: int, limit: int, total: int):
        total_pages = math.ceil(total / limit) if total > 0 else 0
        return cls(
            items=items,
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        )
