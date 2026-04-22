import uuid as uuid_pkg
from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

class UUIDMixin:
    """Provides a UUID primary key for models"""
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(
        primary_key=True, default=uuid_pkg.uuid4
    )

class TimestampMixin:
    """Provides created_at and updated_at timestamps"""
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )