from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import AsyncSessionLocal


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # Якщо виконання ендпоінту завершилось без помилок:
            await session.commit()
        except Exception:
            # Якщо в ендпоінті сталася помилка (будь-яка):
            await session.rollback()
            raise  # Прокидаємо помилку далі, щоб FastAPI повернув 500 або обробив її
        finally:
            # Закриття сесії гарантоване (повертає з'єднання в пул)
            await session.close()


SessionDep = Annotated[AsyncSession, Depends(get_db)]
