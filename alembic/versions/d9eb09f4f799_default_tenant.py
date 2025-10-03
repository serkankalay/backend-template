"""default tenant

Revision ID: d9eb09f4f799
Revises: e6c3ff258c30
Create Date: 2025-10-03 22:07:28.779069

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd9eb09f4f799'
down_revision: Union[str, None] = 'e6c3ff258c30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE SCHEMA IF NOT EXISTS "tenant_default";')
    op.execute(
        sa.text(
            """
            insert into shared.tenant (name, schema, default_tenant, active) 
            values ('Default Tenant', 'tenant_default', TRUE, TRUE)
            """
        )
    )
    op.execute(
        sa.text(
            """
            insert into shared.user (tenant_id, name, password, email, active)
            values (1000, 'User', 'super_secret_password', 'hello@tenant.com', TRUE)
            """
        )
    )


def downgrade() -> None:
    # Delete the row we inserted
    op.execute(
        sa.text(
            """
            DELETE
            FROM shared.tenant
            WHERE name = 'Default Tenant'
              AND schema = 'tenant_default'
            """
        )
    )
    op.execute(
        sa.text(
            """
            DELETE
            FROM shared.user
            WHERE name = 'User'
              AND tenant_id = 1000
            """
        )
    )

    # Drop the schema we created (CASCADE ensures no leftover objects block it)
    op.execute('DROP SCHEMA IF EXISTS "tenant_default" CASCADE;')
