from typing_extensions import Annotated
import urllib

from src.core.config import ALLOWED_MIME_TYPES, BASE_DIR, MAX_FILE_SIZE, UPLOAD_DIR
from fastapi import HTTPException, HTTPException, Request, UploadFile
from uuid import uuid4
import shutil
import os
from sqlalchemy import select

from src.api.dependencies import SessionDep
from src.domain.blog.models import Post
from src.domain.blog.schemas import PostCreate

FULL_UPLOAD_PATH = BASE_DIR / UPLOAD_DIR


async def get_posts(session: SessionDep):
    stmt = select(Post)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_post(session: SessionDep, post_in: PostCreate, image: UploadFile | None, request: Request):
    image_url_for_db = None

    if image:
        # --- БЛОК СУВОРІЙ ВАЛІДАЦІЇ ---

        # 1. Перевірка MIME-типу
        if image.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Недопустимий тип файлу: {image.content_type}. Дозволені: JPEG, PNG, WEBP, GIF."
            )

        # 2. Перевірка розміру файлу (У FastAPI >= 0.88.0 є атрибут size)
        if image.size and image.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Файл занадто великий. Максимальний розмір: 5 МБ."
            )

        # 3. Додатковий захист: перевірка розширення (щоб уникнути .php файлів з підробленим MIME)
        ext = image.filename.split(".")[-1].lower()
        if ext not in ["jpg", "jpeg", "png", "webp", "gif"]:
            raise HTTPException(
                status_code=400,
                detail="Недопустиме розширення файлу."
            )

        # --- КІНЕЦЬ ВАЛІДАЦІЇ ---

        os.makedirs(FULL_UPLOAD_PATH, exist_ok=True)
        file_name = f"{uuid4()}.{ext}"
        save_path = FULL_UPLOAD_PATH / file_name

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Зберігаємо ПОВНИЙ шлях у базу!
        image_url_for_db = f"{request.base_url}static/uploads/posts/{file_name}"

    new_post = Post(
        **post_in.model_dump(),
        image_path=image_url_for_db
    )

    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)
    return new_post


async def get_post_by_id(session: SessionDep, post_id: int):
    stmt = select(Post).where(Post.id == post_id)
    result = await session.execute(stmt)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


async def update_post(session: SessionDep, post_id: int, post_in: PostCreate):
    stmt = select(Post).where(Post.id == post_id)
    result = await session.execute(stmt)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    for key, value in post_in.model_dump().items():
        setattr(post, key, value)

    await session.commit()
    await session.refresh(post)
    return post


async def delete_post(session: SessionDep, post_id: int):
    stmt = select(Post).where(Post.id == post_id)
    result = await session.execute(stmt)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.image_path:
        # 1. Розбираємо URL на частини і беремо ТІЛЬКИ шлях
        # З "http://127.0.0.1:8001/static/..." отримаємо "/static/..."
        parsed_url = urllib.parse.urlparse(post.image_path)
        url_path_only = parsed_url.path

        # 2. Відрізаємо перший слеш для коректного об'єднання з BASE_DIR
        relative_path = url_path_only.lstrip("/")
        file_path = BASE_DIR / relative_path

        # 3. Видаляємо файл, якщо він існує
        if file_path.exists():
            file_path.unlink()
        else:
            # Аналітична порада: логуй такі випадки, щоб відстежувати розсинхронізацію БД і диска
            print(
                f"WARNING: Відсутній файл на диску при видаленні поста: {file_path}")

    await session.delete(post)
    await session.commit()
    return post


async def delete_all_posts(session: SessionDep):
    stmt = select(Post)
    result = await session.execute(stmt)
    posts = result.scalars().all()

    for post in posts:
        if post.image_path:
            # 1. Безпечно витягуємо лише шлях (навіть якщо там повний URL з http://)
            parsed_url = urllib.parse.urlparse(post.image_path)
            url_path_only = parsed_url.path

            # 2. Формуємо валідний шлях для операційної системи
            relative_path = url_path_only.lstrip("/")
            file_path = BASE_DIR / relative_path

            # 3. Видаляємо фізичний файл
            if file_path.exists():
                file_path.unlink()
            else:
                # Корисно для дебагу, якщо база і диск розсинхронізувалися
                print(
                    f"WARNING: Файл не знайдено при масовому видаленні: {file_path}")

        # Видаляємо запис з бази
        await session.delete(post)

    await session.commit()
    return True
