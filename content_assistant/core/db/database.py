from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from content_assistant.core.config.settings import get_settings
import contextlib

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


@contextlib.asynccontextmanager
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db
