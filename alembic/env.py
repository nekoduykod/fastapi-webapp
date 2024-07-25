from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Add the base directory to the system path
sys.path.append(BASE_DIR)

# Alembic Config object which provides access to the values within the .ini file
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import the model's MetaData object here
# Update the import path to your actual model's file
import app.models.models as models
target_metadata = models.Base.metadata

# Set the SQLite URL
config.set_main_option("sqlalchemy.url", os.environ.get("SQLITE_URL", "sqlite:///./test.db"))

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
