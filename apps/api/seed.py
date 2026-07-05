"""
Database seeder — creates the ForgeAI master account.

Run with:
    docker-compose exec api python seed.py
"""

import asyncio
import sys
import os

sys.path.insert(0, "/app")

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from src.core.security import get_password_hash
from src.models.user import User, UserRole, UserStatus
from src.models.preferences import UserPreferences
from src.core.config import settings

MASTER_EMAIL    = "forgeai@gmail.com"
MASTER_USERNAME = "forgeai"
MASTER_NAME     = "ForgeAI Master"
MASTER_PASSWORD = "123"

async def seed():
    # Ensure we are using the async driver for the seeder
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # Check if master account already exists
        result = await db.execute(select(User).where(User.email == MASTER_EMAIL))
        existing = result.scalar_one_or_none()

        if existing:
            print(f"\n[seed] Master account already exists → {MASTER_EMAIL}\n")
            return

        user = User(
            email=MASTER_EMAIL,
            username=MASTER_USERNAME,
            full_name=MASTER_NAME,
            password_hash=get_password_hash(MASTER_PASSWORD),
            role=UserRole.OWNER,
            status=UserStatus.ACTIVE,
            email_verified=True,
        )
        db.add(user)
        await db.flush()

        prefs = UserPreferences(user_id=user.id, theme="dark")
        db.add(prefs)
        await db.commit()

        print(f"""
╔══════════════════════════════════════════════╗
║        ForgeAI Master Account Created        ║
╠══════════════════════════════════════════════╣
║  Email    : {MASTER_EMAIL:<33}║
║  Password : {MASTER_PASSWORD:<33}║
║  Role     : OWNER                            ║
╚══════════════════════════════════════════════╝
""")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())
