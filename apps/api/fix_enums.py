import asyncio
import sys
sys.path.insert(0, "/app")

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from src.core.config import settings

async def fix_enums():
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
    engine = create_async_engine(db_url, echo=False)
    
    # Missing WorkflowStatus values
    new_workflow_statuses = ["CREATED", "PLANNING", "READY", "WAITING_FOR_APPROVAL"]
    
    async with engine.begin() as conn:
        for status in new_workflow_statuses:
            try:
                await conn.execute(text(f"ALTER TYPE workflowstatus ADD VALUE IF NOT EXISTS '{status}';"))
                print(f"Added '{status}' to workflowstatus")
            except Exception as e:
                print(f"Skipping '{status}' (might already exist): {e}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix_enums())
