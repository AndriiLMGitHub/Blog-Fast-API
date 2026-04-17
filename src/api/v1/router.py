from fastapi import APIRouter
from src.domain.blog.routes import router as blog_router

v1_router = APIRouter(prefix="/v1", tags=["API v1 Blog"])

# Включаємо маршрути блогу в основний роутер API v1
v1_router.include_router(blog_router)
