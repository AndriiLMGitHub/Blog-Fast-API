from __future__ import annotations

from typing import Generic, List, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

DataT = TypeVar("DataT")


# ─── Generic envelope ───────────────────────────────────────────────
class APIResponse(BaseModel, Generic[DataT]):
    message: str
    data: DataT


class PaginatedResponse(BaseModel, Generic[DataT]):
    message: str
    data: List[DataT]


# ─── Domain models ──────────────────────────────────────────────────
class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=512)
    content: str | None = Field(default=None, max_length=100_000)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be blank")
        return v.strip()


class Post(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # дозволяє і alias, і field name
    )

    id: int
    title: str
    content: str | None = None
    image_url: str | None = Field(default=None, alias="image_path")


# ─── Typed response aliases (zero duplication) ──────────────────────
PostResponse = APIResponse[Post]
PostListResponse = PaginatedResponse[Post]
PostCreateResponse = APIResponse[Post]
PostDeleteResponse = APIResponse[None]
