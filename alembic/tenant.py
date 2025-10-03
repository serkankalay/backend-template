import functools
from typing import Callable

from sqlalchemy import text
from typeguard import typechecked
from alembic import op


@typechecked
def for_each_tenant(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapped():
        schemas = op.get_bind().execute(text("SELECT schema FROM shared.tenant")).fetchall()
        for (schema,) in schemas:
            func(schema=schema)

    return wrapped