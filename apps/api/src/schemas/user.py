from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
import uuid
from datetime import datetime
import re

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str | None = None

class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number.")
        return v

class UserResponse(UserBase):
    id: uuid.UUID
    avatar_url: str | None = None
    role: str
    status: str
    email_verified: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
