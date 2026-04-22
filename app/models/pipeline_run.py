from datetime import datetime
import uuid as uuid_pkg
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin


class PipelineRun(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "pipeline_runs"

    profile_uuid: Mapped[uuid_pkg.UUID] = mapped_column(ForeignKey("business_profiles.uuid"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    queries_discovered: Mapped[int] = mapped_column(Integer, default=0)
    queries_scored: Mapped[int] = mapped_column(Integer, default=0)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    profile = relationship("BusinessProfile", back_populates="pipeline_runs")
    queries = relationship("DiscoveredQuery", back_populates="run", cascade="all, delete-orphan")