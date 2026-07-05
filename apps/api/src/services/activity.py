from sqlalchemy.ext.asyncio import AsyncSession
from src.models.activity import Activity
from src.schemas.activity import ActivityCreate
from uuid import UUID

async def log_activity(db: AsyncSession, activity_in: ActivityCreate) -> Activity:
    activity = Activity(
        project_id=activity_in.project_id,
        user_id=activity_in.user_id,
        event=activity_in.event,
        resource=activity_in.resource,
        metadata_json=activity_in.metadata_json
    )
    db.add(activity)
    # We do not commit here to allow caller transaction scope
    await db.flush()
    return activity
