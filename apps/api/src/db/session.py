from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.core.config import settings

# SQLAlchemy requires the async driver for postgres
async_db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    async_db_url, 
    echo=(settings.ENVIRONMENT == "development")
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False, 
    autoflush=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
