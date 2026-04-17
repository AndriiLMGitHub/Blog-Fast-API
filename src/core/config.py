import os
from pathlib import Path
from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 1. Динамічно визначаємо корінь проєкту.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

UPLOAD_DIR = "static/uploads/posts"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Дозволені MIME-типи для зображень
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp", "image/gif"]
# Максимальний розмір файлу (5 МБ)
MAX_FILE_SIZE = 5 * 1024 * 1024


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # 2. Будуємо абсолютний шлях від кореня проєкту
    DB_PATH: Path = Field(default=BASE_DIR / "db.sqlite3")

    DB_ECHO: bool = False
    DEBUG: bool
    SECRET_KEY: str

    HOST: str = "127.0.0.1"

    @field_validator("DB_PATH")
    @classmethod
    def ensure_directory_exists(cls, v: Path) -> Path:
        v.parent.mkdir(parents=True, exist_ok=True)
        return v

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        # Звертаємось до поля класу через self
        return f"sqlite+aiosqlite:///{self.DB_PATH.absolute()}"

    @computed_field
    @property
    def SYNC_DATABASE_URL(self) -> str:
        return f"sqlite:///{self.DB_PATH.absolute()}"


settings = Settings()
