from fastapi import APIRouter
from src.api.v1.router import v1_router

api_router = APIRouter(
    prefix="/api",
)

# Включаємо маршрути API v1 в основний роутер
api_router.include_router(v1_router)
