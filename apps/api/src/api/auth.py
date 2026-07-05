from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db
from src.schemas.user import UserCreate, UserResponse
from src.schemas.auth import Token, LoginRequest, RefreshRequest
from src.services.auth import register_user, authenticate_user, create_user_session, refresh_tokens, logout_user
from src.core.security import create_access_token
from src.api.deps import get_current_active_user
from src.models.user import User
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(request: Request, user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    return await register_user(db, user_in)

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, req: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, req.email, req.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if user.status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
        
    access_token = create_access_token(subject=str(user.id))
    refresh_token = await create_user_session(
        db=db, 
        user_id=user.id, 
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh(req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    tokens = await refresh_tokens(db, req.refresh_token)
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    await logout_user(db, req.refresh_token)
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user
