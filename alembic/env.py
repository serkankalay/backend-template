from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, MetaData
from sqlalchemy import pool
import sqlalchemy as sa
from sqlalchemy.engine.url import make_url

from alembic import context

load_dotenv()

from src.settings import Settings

config = context.config
config.set_main_option(
    "sqlalchemy.url",
    Settings.database.pg_dsn.unicode_string(),
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from src.data_model import Base


def _emit_shared_schema_offline() -> None:
    """Emit CREATE SCHEMA for offline SQL generation when using Postgres."""
    url = make_url(config.get_main_option("sqlalchemy.url"))
    if url.get_backend_name() == "postgresql":
        schema = Settings.database.shared_schema
        # Quoted to be safe with casing/special chars
        context.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}";')


def _ensure_shared_schema_online(connection) -> None:
    """Create the shared schema before Alembic tries to create alembic_version."""
    schema = Settings.database.shared_schema
    dialect = connection.dialect.name

    if not schema:
        return

    if dialect == "postgresql":
        # Use IF NOT EXISTS for idempotency; wrap in its own transaction and commit.
        with connection.begin():
            connection.exec_driver_sql(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
    else:
        # Best-effort generic path (no IF NOT EXISTS). Ignore if not supported.
        try:
            with connection.begin():
                connection.execute(sa.schema.CreateSchema(schema))
        except Exception:
            pass


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")

    # Tell Alembic to store the version table in the shared schema
    context.configure(
        url=url,
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=Settings.database.shared_schema,
    )

    # Emit the CREATE SCHEMA ahead of everything else (for Postgres)
    _emit_shared_schema_offline()

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    naming_convention = {
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
    translated = MetaData(naming_convention=naming_convention)

    for table in Base.metadata.tables.values():
        if table.schema == Settings.database.shared_schema:
            continue
        table.to_metadata(translated)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Ensure the schema exists *before* Alembic tries to create alembic_version
        _ensure_shared_schema_online(connection)

        context.configure(
            connection=connection,
            target_metadata=translated,
            compare_type=True,
            transaction_per_migration=True,
            version_table_schema=Settings.database.shared_schema,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
