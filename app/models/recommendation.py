import uuid as uuid_pkg

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ContentRecommendation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "content_recommendations"

    profile_uuid: Mapped[uuid_pkg.UUID] = mapped_column(
        ForeignKey("business_profiles.uuid"), nullable=False
    )
    query_uuid: Mapped[uuid_pkg.UUID] = mapped_column(
        ForeignKey("discovered_queries.uuid"), nullable=False
    )

    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    rationale: Mapped[str] = mapped_column(String, nullable=False)
    target_keywords: Mapped[list[str]] = mapped_column(JSON, default=list)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)

    query = relationship("DiscoveredQuery", back_populates="recommendations")
