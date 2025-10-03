"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

from alembic_multi_tenancy.tenant import for_each_tenant

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


@for_each_tenant
def upgrade(schema: str) -> None:
    op.get_bind().execute(sa.text(f"SET SEARCH_PATH={schema};"))
    ${upgrades if upgrades else "pass"}


@for_each_tenant
def downgrade(schema: str) -> None:
    op.get_bind().execute(sa.text(f"SET SEARCH_PATH={schema};"))
    ${downgrades if downgrades else "pass"}
