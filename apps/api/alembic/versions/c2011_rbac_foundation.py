"""RBAC platform foundation

Revision ID: c2011_rbac_foundation
Revises: 5a7c91e2d4f8
"""

import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "c2011_rbac_foundation"
down_revision = "5a7c91e2d4f8"
branch_labels = None
depends_on = None


PLATFORM_ROLES = [
    (
        "platform_super_admin",
        "SUPER_ADMIN",
        "Acces complet la administrarea platformei ContaAI",
    ),
    (
        "platform_admin",
        "ADMIN",
        "Acces la funcțiile administrative delegate",
    ),
    (
        "platform_client",
        "CLIENT",
        "Utilizator standard al platformei ContaAI",
    ),
]


PLATFORM_PERMISSIONS = [
    ("platform.access", "Acces la platforma ContaAI"),
    ("developer.view", "Vizualizare Developer Center"),
    ("developer.manage", "Administrare Developer Center"),
    ("users.view", "Vizualizare utilizatori platformă"),
    ("users.manage", "Administrare utilizatori platformă"),
    ("roles.view", "Vizualizare roluri și permisiuni"),
    ("roles.manage", "Administrare roluri și permisiuni"),
    ("audit.view", "Vizualizare jurnal de audit"),
    ("system.view", "Vizualizare stare sistem"),
    ("system.manage", "Administrare setări sistem"),
]


PLATFORM_ROLE_PERMISSIONS = {
    "platform_super_admin": [
        permission[0] for permission in PLATFORM_PERMISSIONS
    ],
    "platform_admin": [
        "platform.access",
        "developer.view",
        "developer.manage",
        "system.view",
    ],
    "platform_client": [
        "platform.access",
    ],
}


def upgrade() -> None:
    op.add_column(
        "roles",
        sa.Column(
            "scope",
            sa.String(length=20),
            nullable=False,
            server_default="organization",
        ),
    )
    op.create_index(
        "ix_roles_scope",
        "roles",
        ["scope"],
        unique=False,
    )
    op.create_check_constraint(
        "ck_roles_scope",
        "roles",
        "scope IN ('platform', 'organization')",
    )

    op.add_column(
        "permissions",
        sa.Column(
            "scope",
            sa.String(length=20),
            nullable=False,
            server_default="organization",
        ),
    )
    op.create_index(
        "ix_permissions_scope",
        "permissions",
        ["scope"],
        unique=False,
    )
    op.create_check_constraint(
        "ck_permissions_scope",
        "permissions",
        "scope IN ('platform', 'organization')",
    )

    op.create_table(
        "user_platform_roles",
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
            "role_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "created_by_user_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "role_id",
            name="uq_user_platform_role",
        ),
    )

    op.create_index(
        "ix_user_platform_roles_user_id",
        "user_platform_roles",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_user_platform_roles_role_id",
        "user_platform_roles",
        ["role_id"],
        unique=False,
    )
    op.create_index(
        "ix_user_platform_roles_created_by_user_id",
        "user_platform_roles",
        ["created_by_user_id"],
        unique=False,
    )

    connection = op.get_bind()

    role_ids = {}
    permission_ids = {}

    for key, name, description in PLATFORM_ROLES:
        role_id = uuid.uuid4()

        connection.execute(
            sa.text(
                """
                INSERT INTO roles (
                    id,
                    key,
                    name,
                    description,
                    scope
                )
                VALUES (
                    :id,
                    :key,
                    :name,
                    :description,
                    'platform'
                )
                """
            ),
            {
                "id": role_id,
                "key": key,
                "name": name,
                "description": description,
            },
        )

        role_ids[key] = role_id

    for key, name in PLATFORM_PERMISSIONS:
        permission_id = uuid.uuid4()

        connection.execute(
            sa.text(
                """
                INSERT INTO permissions (
                    id,
                    key,
                    name,
                    scope
                )
                VALUES (
                    :id,
                    :key,
                    :name,
                    'platform'
                )
                """
            ),
            {
                "id": permission_id,
                "key": key,
                "name": name,
            },
        )

        permission_ids[key] = permission_id

    for role_key, permission_keys in PLATFORM_ROLE_PERMISSIONS.items():
        for permission_key in permission_keys:
            connection.execute(
                sa.text(
                    """
                    INSERT INTO role_permissions (
                        id,
                        role_id,
                        permission_id
                    )
                    VALUES (
                        :id,
                        :role_id,
                        :permission_id
                    )
                    """
                ),
                {
                    "id": uuid.uuid4(),
                    "role_id": role_ids[role_key],
                    "permission_id": permission_ids[permission_key],
                },
            )


def downgrade() -> None:
    connection = op.get_bind()

    for role_key, _, _ in PLATFORM_ROLES:
        connection.execute(
            sa.text(
                """
                DELETE FROM role_permissions
                WHERE role_id = (
                    SELECT id
                    FROM roles
                    WHERE key = :role_key
                )
                """
            ),
            {"role_key": role_key},
        )

    for permission_key, _ in PLATFORM_PERMISSIONS:
        connection.execute(
            sa.text(
                """
                DELETE FROM role_permissions
                WHERE permission_id = (
                    SELECT id
                    FROM permissions
                    WHERE key = :permission_key
                )
                """
            ),
            {"permission_key": permission_key},
        )

    op.drop_index(
        "ix_user_platform_roles_created_by_user_id",
        table_name="user_platform_roles",
    )
    op.drop_index(
        "ix_user_platform_roles_role_id",
        table_name="user_platform_roles",
    )
    op.drop_index(
        "ix_user_platform_roles_user_id",
        table_name="user_platform_roles",
    )
    op.drop_table("user_platform_roles")

    for role_key, _, _ in PLATFORM_ROLES:
        connection.execute(
            sa.text(
                "DELETE FROM roles WHERE key = :role_key"
            ),
            {"role_key": role_key},
        )

    for permission_key, _ in PLATFORM_PERMISSIONS:
        connection.execute(
            sa.text(
                "DELETE FROM permissions WHERE key = :permission_key"
            ),
            {"permission_key": permission_key},
        )

    op.drop_constraint(
        "ck_permissions_scope",
        "permissions",
        type_="check",
    )
    op.drop_index(
        "ix_permissions_scope",
        table_name="permissions",
    )
    op.drop_column(
        "permissions",
        "scope",
    )

    op.drop_constraint(
        "ck_roles_scope",
        "roles",
        type_="check",
    )
    op.drop_index(
        "ix_roles_scope",
        table_name="roles",
    )
    op.drop_column(
        "roles",
        "scope",
    )
