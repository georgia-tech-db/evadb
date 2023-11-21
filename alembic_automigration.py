from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.migration import MigrationContext
from sqlalchemy import create_engine
from pathlib import Path
import evadb


def get_current_revision(db_uri):
    engine = create_engine(db_uri)
    conn = engine.connect()
    context = MigrationContext.configure(conn)
    return context.get_current_revision()

def get_latest_revision(config):
    script = ScriptDirectory.from_config(config)
    return script.get_heads()[-1]

def run_migrations():
    # Set up database connnection
    db_uri = evadb.database.get_default_db_uri(Path('evadb_data'))
    alembic_cfg = Config('./alembic.ini')
    alembic_cfg.set_main_option('sqlalchemy.url', db_uri)
    
    # Get current local revision and lastest revision available
    current_revision = get_current_revision(db_uri)
    latest_revision = get_latest_revision(alembic_cfg)
    
    # If newer revision found, upgrade to the lastest revision
    if current_revision and current_revision != latest_revision:
        command.upgrade(alembic_cfg, latest_revision)

if __name__ == "__main__":
    run_migrations()