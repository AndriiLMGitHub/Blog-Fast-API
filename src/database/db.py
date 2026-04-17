from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.core.config import settings

# Create an asynchronous engine using the database URL from the environment variable. The echo parameter is set to True to log all SQL statements.
engine = create_async_engine(
    settings.DATABASE_URL,
    # echo=True, # Включаємо логування SQL-запитів для налагодження
    # future=True,  # Використовуємо режим майбутнього для сумісності з SQLAlchemy 2.0
)

# AsyncSessionLocal is a factory for creating new AsyncSession instances. It is configured to use the engine we created and to not expire objects on commit.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
