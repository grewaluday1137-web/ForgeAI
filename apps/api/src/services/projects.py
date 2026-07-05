from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exc
from src.models.project import Project, ProjectMember
from src.models.enums import ProjectPermission
from src.schemas.project import ProjectCreate
from src.services.activity import log_activity
from src.schemas.activity import ActivityCreate
from src.websocket.manager import manager
from slugify import slugify
from fastapi import HTTPException, status
from uuid import UUID

async def create_project(db: AsyncSession, project_in: ProjectCreate, current_user_id: UUID) -> Project:
    # 1. Generate unique slug
    base_slug = slugify(project_in.name)
    slug = base_slug
    
    counter = 1
    while True:
        result = await db.execute(select(Project).where(Project.slug == slug))
        if not result.scalar_one_or_none():
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    # 2. Create Project
    project = Project(
        owner_id=current_user_id,
        name=project_in.name,
        slug=slug,
        description=project_in.description,
        icon=project_in.icon,
        color=project_in.color,
        visibility=project_in.visibility,
        created_by=current_user_id,
        updated_by=current_user_id
    )
    db.add(project)
    await db.flush()

    # 3. Create ProjectMember (Owner)
    member = ProjectMember(
        project_id=project.id,
        user_id=current_user_id,
        permissions=ProjectPermission.OWNER
    )
    db.add(member)
    
    # 4. Log Activity
    await log_activity(db, ActivityCreate(
        project_id=project.id,
        user_id=current_user_id,
        event="project.created",
        resource="project",
        metadata_json={"name": project.name, "slug": project.slug}
    ))

    await db.commit()
    await db.refresh(project)

    # 5. Broadcast WebSocket event
    await manager.broadcast_event("project.created", {
        "id": str(project.id),
        "name": project.name,
        "owner_id": str(project.owner_id)
    })

    return project

async def get_projects(db: AsyncSession, current_user_id: UUID) -> list[Project]:
    # For now, return projects where user is owner or member
    stmt = select(Project).join(ProjectMember).where(ProjectMember.user_id == current_user_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_project(db: AsyncSession, project_id: UUID, current_user_id: UUID) -> Project:
    stmt = select(Project).join(ProjectMember).where(Project.id == project_id, ProjectMember.user_id == current_user_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project

async def get_project_by_slug(db: AsyncSession, slug: str, current_user_id: UUID) -> Project:
    stmt = select(Project).join(ProjectMember).where(Project.slug == slug, ProjectMember.user_id == current_user_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project
