from logging.config import dictConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from content_assistant.core.models import Base
from content_assistant.core.config.logging import logging_config
from content_assistant.core.config.settings import get_settings
import logging

# Create a logger instance
logger = logging.getLogger('alembic.runtime.migration')

# Get settings instance
settings = get_settings()

# this is the Alembic Config object
config = context.config

# Construct the SQLAlchemy URL
db_url = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
# Override sqlalchemy.url in alembic.ini
config.set_main_option("sqlalchemy.url", db_url)


dictConfig(logging_config)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()
        logger.info("Alembic upgrade (offline) applied successfully.")


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()
            logger.info("Alembic upgrade applied successfully.")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
