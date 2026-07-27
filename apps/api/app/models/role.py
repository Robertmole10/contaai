import uuid

from sqlalchemy import CheckConstraint, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (
        CheckConstraint(
            "scope IN ('platform', 'organization')",
            name="ck_roles_scope",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    key: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    scope: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="organization",
        server_default="organization",
        index=True,
    )

    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="role",
    )
    permissions: Mapped[list["Permission"]] = relationship(
        secondary="role_permissions",
        back_populates="roles",
        viewonly=True,
    )
    platform_user_assignments: Mapped[list["UserPlatformRole"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
    )
