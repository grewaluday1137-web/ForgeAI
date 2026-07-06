import asyncio
import sys
sys.path.insert(0, "/app")

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from src.core.config import settings

async def check_logs():
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
    engine = create_async_engine(db_url, echo=False)
    
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT level, message, created_at FROM execution_logs ORDER BY created_at DESC LIMIT 10;"))
        for row in result:
            print(f"[{row.created_at}] {row.level}: {row.message}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_logs())
