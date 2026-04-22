from datetime import datetime
import uuid as uuid_pkg
from sqlalchemy import String, ForeignKey, Integer, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin


class DiscoveredQuery(Base, UUIDMixin):
    __tablename__ = "discovered_queries"

    profile_uuid: Mapped[uuid_pkg.UUID] = mapped_column(ForeignKey("business_profiles.uuid"), nullable=False)
    run_uuid: Mapped[uuid_pkg.UUID] = mapped_column(ForeignKey("pipeline_runs.uuid"), nullable=False)

    query_text: Mapped[str] = mapped_column(String, nullable=False)
    estimated_search_volume: Mapped[int] = mapped_column(Integer, nullable=False)
    competitive_difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    opportunity_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    domain_visible: Mapped[bool] = mapped_column(Boolean, nullable=False)
    visibility_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(nullable=False)

    run = relationship("PipelineRun", back_populates="queries")
    recommendations = relationship("ContentRecommendation", back_populates="query", cascade="all, delete-orphan")