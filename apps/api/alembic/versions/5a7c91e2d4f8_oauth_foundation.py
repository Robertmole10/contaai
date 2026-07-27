"""OAuth authentication foundation

Revision ID: 5a7c91e2d4f8
Revises: 4031f498e764
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "5a7c91e2d4f8"
down_revision = "4031f498e764"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(length=255),
        nullable=True,
    )

    op.add_column(
        "users",
        sa.Column(
            "email_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "avatar_url",
            sa.String(length=500),
            nullable=True,
        ),
    )

    op.create_table(
        "user_identities",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "provider",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "provider_user_id",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "provider_email",
            sa.String(length=320),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_user_identities_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_user_identities",
        ),
        sa.UniqueConstraint(
            "provider",
            "provider_user_id",
            name="uq_provider_user",
        ),
    )

    op.create_index(
        "ix_user_identities_user_id",
        "user_identities",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_user_identities_user_id",
        table_name="user_identities",
    )

    op.drop_table("user_identities")

    op.drop_column("users", "avatar_url")
    op.drop_column("users", "email_verified")

    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(length=255),
        nullable=False,
    )
