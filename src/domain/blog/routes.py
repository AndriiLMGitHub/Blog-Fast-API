from fastapi import Request, UploadFile, File, Form
from typing import Annotated

from fastapi import APIRouter

from src.api.dependencies import SessionDep

from src.domain.blog.schemas import PostCreate, PostResponse, PostCreateResponse, PostDeleteResponse, PostListResponse
from src.domain.blog.services import create_post, delete_all_posts, delete_post, get_post_by_id, get_posts, update_post


router = APIRouter(prefix="/posts")


@router.get(
    "/",
    response_model=PostListResponse,
    summary="Get all posts",
    description="Retrieves a list of all blog posts from the database."
)
async def get_posts_router(session: SessionDep):
    posts = await get_posts(session)
    return {"message": "Posts retrieved successfully", "data": posts}


@router.post(
    "/", response_model=PostCreateResponse, summary="Create a new post", description="Creates a new blog post with an optional image upload.")
async def create_post_router(
    session: SessionDep,
    # Використовуємо Form, щоб приймати multipart/form-data
    title: Annotated[str, Form()],
    content: Annotated[str | None, Form()] = None,
    image: Annotated[UploadFile | None, File()] = None,
    new_request: Request = None,  # Додаємо Request для формування URL
):
    # Вручну створюємо схему для валідації (опціонально)
    post_data = PostCreate(title=title, content=content)

    # Передаємо сесію, дані та файл у сервіс
    new_post = await create_post(session, post_data, image, request=new_request)

    return {
        "message": "Post created successfully",
        "data": new_post,
    }


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Get a post by ID",
    description="Retrieves a single blog post by its ID."
)
async def get_post_by_id_router(session: SessionDep, post_id: int):
    post = await get_post_by_id(session, post_id)
    return {"message": "Post retrieved successfully", "data": post}


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    summary="Update a post by ID",
    description="Updates an existing blog post by its ID. (Not implemented yet)"
)
async def update_post_router(session: SessionDep, post_id: int, post_in: Annotated[PostCreate, Form()]):
    # Тут буде логіка оновлення поста, але поки що повертаємо заглушку
    post = await update_post(session, post_id, post_in=post_in)
    return {"message": "Update post functionality is not implemented yet", "data": post}


@router.delete(
    "/{post_id}",
    response_model=PostDeleteResponse,
    summary="Delete a post by ID",
    description="Deletes a post from the database and removes its associated image file if it exists."
)
async def delete_post_router(session: SessionDep, post_id: int, post: PostResponse = None):
    await delete_post(session, post_id)
    return {"message": "Post deleted successfully", "data": None}


@router.delete(
    "/delete/all",
    response_model=PostDeleteResponse,
    summary="Delete all posts",
    description="Deletes all posts from the database and removes all associated image files."
)
async def delete_all_posts_router(session: SessionDep):
    await delete_all_posts(session)
    return {"message": "All posts deleted successfully", "data": None}
