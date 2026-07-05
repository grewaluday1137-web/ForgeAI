from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from redis.asyncio import Redis
from src.db.session import get_db
from src.core.config import settings

router = APIRouter(tags=["health"])

async def get_redis():
    redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield redis
    finally:
        await redis.close()

@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    db_status = "ok"
    redis_status = "ok"

    # Check Database
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    # Check Redis
    try:
        await redis.ping()
    except Exception as e:
        redis_status = f"error: {str(e)}"

    overall_status = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"

    return {
        "status": overall_status,
        "api": "ok",
        "database": db_status,
        "redis": redis_status,
        "environment": settings.ENVIRONMENT
    }
