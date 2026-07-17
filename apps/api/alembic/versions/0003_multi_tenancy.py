"""multi tenancy, roles and permissions"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_multi_tenancy"
down_revision = "0002_authentication"
branch_labels = None
depends_on = None

ROLE_ROWS = [
    ("owner", "Owner", "Control complet asupra organizației"),
    ("admin", "Administrator", "Administrare companii și membri"),
    ("accountant", "Contabil", "Acces operațional contabil"),
    ("auditor", "Auditor", "Acces de citire și audit"),
    ("employee", "Angajat", "Acces limitat la documente"),
]

PERMISSION_ROWS = [
    ("organization.manage", "Administrare organizație"),
    ("company.create", "Creare companie"),
    ("company.read", "Vizualizare companii"),
    ("company.manage", "Administrare companii"),
    ("member.read", "Vizualizare membri"),
    ("member.manage", "Administrare membri"),
    ("document.read", "Vizualizare documente"),
    ("document.manage", "Administrare documente"),
    ("accounting.read", "Vizualizare contabilitate"),
    ("accounting.manage", "Administrare contabilitate"),
    ("report.read", "Vizualizare rapoarte"),
]

ROLE_PERMISSIONS = {
    "owner": [p[0] for p in PERMISSION_ROWS],
    "admin": [p[0] for p in PERMISSION_ROWS],
    "accountant": ["company.read", "member.read", "document.read", "document.manage", "accounting.read", "accounting.manage", "report.read"],
    "auditor": ["company.read", "member.read", "document.read", "accounting.read", "report.read"],
    "employee": ["company.read", "document.read", "document.manage"],
}


def upgrade():
    op.add_column("companies", sa.Column("legal_form", sa.String(64), nullable=True))
    op.add_column("companies", sa.Column("country_code", sa.String(2), nullable=False, server_default="RO"))
    op.create_index("ix_companies_organization_id", "companies", ["organization_id"])
    op.create_index("ix_companies_tax_id", "companies", ["tax_id"])

    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
    )
    op.create_index("ix_roles_key", "roles", ["key"], unique=True)

    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(100), nullable=False, unique=True),
        sa.Column("name", sa.String(150), nullable=False),
    )
    op.create_index("ix_permissions_key", "permissions", ["key"], unique=True)

    op.create_table(
        "memberships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "organization_id", name="uq_user_organization"),
    )
    op.create_index("ix_memberships_user_id", "memberships", ["user_id"])
    op.create_index("ix_memberships_organization_id", "memberships", ["organization_id"])
    op.create_index("ix_memberships_role_id", "memberships", ["role_id"])

    op.create_table(
        "role_permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    conn = op.get_bind()
    role_ids = {}
    permission_ids = {}
    for key, name, description in ROLE_ROWS:
        role_id = conn.execute(sa.text("SELECT gen_random_uuid()" )).scalar_one()
        conn.execute(sa.text("INSERT INTO roles (id, key, name, description) VALUES (:id, :key, :name, :description)"), {"id": role_id, "key": key, "name": name, "description": description})
        role_ids[key] = role_id
    for key, name in PERMISSION_ROWS:
        permission_id = conn.execute(sa.text("SELECT gen_random_uuid()" )).scalar_one()
        conn.execute(sa.text("INSERT INTO permissions (id, key, name) VALUES (:id, :key, :name)"), {"id": permission_id, "key": key, "name": name})
        permission_ids[key] = permission_id
    for role_key, permission_keys in ROLE_PERMISSIONS.items():
        for permission_key in permission_keys:
            conn.execute(sa.text("INSERT INTO role_permissions (id, role_id, permission_id) VALUES (gen_random_uuid(), :role_id, :permission_id)"), {"role_id": role_ids[role_key], "permission_id": permission_ids[permission_key]})


def downgrade():
    op.drop_table("role_permissions")
    op.drop_index("ix_memberships_role_id", table_name="memberships")
    op.drop_index("ix_memberships_organization_id", table_name="memberships")
    op.drop_index("ix_memberships_user_id", table_name="memberships")
    op.drop_table("memberships")
    op.drop_index("ix_permissions_key", table_name="permissions")
    op.drop_table("permissions")
    op.drop_index("ix_roles_key", table_name="roles")
    op.drop_table("roles")
    op.drop_index("ix_companies_tax_id", table_name="companies")
    op.drop_index("ix_companies_organization_id", table_name="companies")
    op.drop_column("companies", "country_code")
    op.drop_column("companies", "legal_form")
