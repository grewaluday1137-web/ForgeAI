from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from redis.asyncio import Redis
from src.core.config import settings
from src.core.exceptions import (
    AppException, app_exception_handler,
    validation_exception_handler, unhandled_exception_handler
)
from src.core.middleware import SecurityHeadersMiddleware
from src.api.health import router as health_router
from src.api.auth import router as auth_router
from src.api.testing import router as testing_router
from src.api.ws import router as ws_router
from src.api.projects import router as projects_router
from src.api.repositories import router as repositories_router
from src.api.workspaces import router as workspaces_router
from src.api.workflows import router as workflows_router
from src.api.tasks import router as tasks_router

# ─── Rate Limiter (shared across routers) ────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify Redis connection on startup
    redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        await redis.ping()
        print("\n=== Successfully connected to Redis on startup! ===\n")
    except Exception as e:
        print(f"\n=== WARNING: Failed to connect to Redis on startup: {e} ===\n")
    finally:
        await redis.close()
    
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    # Hide tech stack details in production
    docs_url=f"{settings.API_V1_STR}/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url=f"{settings.API_V1_STR}/redoc" if settings.ENVIRONMENT != "production" else None,
)

# ─── State ────────────────────────────────────────────────────────────────────
app.state.limiter = limiter

# ─── Middleware (applied in reverse order, last = outermost) ─────────────────
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# ─── Exception Handlers ───────────────────────────────────────────────────────
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# ─── Routers ─────────────────────────────────────────────────────────────────
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(ws_router, prefix=settings.API_V1_STR)
app.include_router(projects_router, prefix=settings.API_V1_STR)
app.include_router(testing_router, prefix=settings.API_V1_STR)
app.include_router(repositories_router, prefix=settings.API_V1_STR)
app.include_router(workspaces_router, prefix=settings.API_V1_STR)
app.include_router(workflows_router, prefix=settings.API_V1_STR)
app.include_router(tasks_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": f"{settings.PROJECT_NAME} API is running"}
