from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.core.config import settings

from src.api.main_router import api_router


app = FastAPI(
    title="Blog API",
    description="A simple API for managing blog posts with image uploads.",
    version="1.0.0",
    docs_url="/",
)

app.include_router(api_router)

# Монтуємо папку uploads як статичний ресурс
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=8001,
        log_level="info",
        reload=True,
    )
