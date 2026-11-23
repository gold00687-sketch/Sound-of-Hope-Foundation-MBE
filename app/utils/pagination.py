import math
from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

T = TypeVar("T")


class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number (1-based)"),
        page_size: int = Query(
            DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Items per page"
        ),
    ) -> None:
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PageMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int

    @classmethod
    def from_params(cls, params: PaginationParams, total: int) -> "PageMeta":
        return cls(
            page=params.page,
            page_size=params.page_size,
            total=total,
            total_pages=max(1, math.ceil(total / params.page_size)),
        )


class Page(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMeta

    @classmethod
    def create(cls, items: list[T], params: PaginationParams, total: int) -> "Page[T]":
        return cls(items=items, meta=PageMeta.from_params(params, total))
