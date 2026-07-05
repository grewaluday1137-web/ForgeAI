import uuid
from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from src.models.base import Base

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    theme: Mapped[str] = mapped_column(String(50), default="system", nullable=False)
    accent_color: Mapped[str] = mapped_column(String(50), default="blue", nullable=False)
    
    editor_font_size: Mapped[int] = mapped_column(Integer, default=14, nullable=False)
    editor_font: Mapped[str] = mapped_column(String(100), default="Geist Mono", nullable=False)
    editor_tab_size: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="preferences")
