from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)

    # Зберігаємо лише відносний шлях до файлу
    image_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
