# coding=utf-8
import unittest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from test.util import get_evadb_for_testing, shutdown_ray
from evadb.configuration.constants import EvaDB_ROOT_DIR

class TestAlembicMigration(unittest.TestCase):
    def setUp(self):
        # Assume self.evadb is already set up with a connection URI or engine
        self.evadb = get_evadb_for_testing()

        # Configure the Alembic config to point to your test database
        self.alembic_cfg = Config(f"{EvaDB_ROOT_DIR}/alembic.ini")
        self.alembic_cfg.set_main_option('sqlalchemy.url', self.evadb.catalog_uri)

        # Run the migration to add the column
        command.upgrade(self.alembic_cfg, 'e6dc73b305fe')

    def tearDown(self):
        # Optionally, revert the database to the base state
        command.downgrade(self.alembic_cfg, 'base')
        shutdown_ray()

    def test_column_added(self):
        # Use SQLAlchemy to inspect the table and check if the new column exists
        engine = create_engine(self.evadb.catalog_uri)
        inspector = inspect(engine)
        columns = inspector.get_columns('table_catalog')
        column_names = [column['name'] for column in columns]

        self.assertIn('TEST', column_names)

if __name__ == "__main__":
    unittest.main()
