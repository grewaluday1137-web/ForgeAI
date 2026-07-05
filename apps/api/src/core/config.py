from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ForgeAI"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str
    REDIS_URL: str
    ENVIRONMENT: str = "development"
    
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    LOGIN_RATE_LIMIT: str = "10/minute"
    GEMINI_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")


settings = Settings()
