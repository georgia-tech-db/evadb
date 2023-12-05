# coding=utf-8
# Copyright 2018-2023 EvaDB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import unittest
from test.util import get_evadb_for_testing, shutdown_ray

from sqlalchemy import create_engine, inspect

from alembic import command
from alembic.config import Config
from evadb.configuration.constants import EvaDB_ROOT_DIR


class TestAlembicMigration(unittest.TestCase):
    def setUp(self):
        # Assume self.evadb is already set up with a connection URI or engine
        self.evadb = get_evadb_for_testing()

        # Configure the Alembic config to point to your test database
        self.alembic_cfg = Config(f"{EvaDB_ROOT_DIR}/alembic.ini")
        self.alembic_cfg.set_main_option("sqlalchemy.url", self.evadb.catalog_uri)

        # Run the migration to add the column
        command.upgrade(self.alembic_cfg, "e6dc73b305fe")

    def tearDown(self):
        # Optionally, revert the database to the base state
        command.downgrade(self.alembic_cfg, "base")
        shutdown_ray()

    def test_column_added(self):
        # Use SQLAlchemy to inspect the table and check if the new column exists
        engine = create_engine(self.evadb.catalog_uri)
        inspector = inspect(engine)
        columns = inspector.get_columns("table_catalog")
        column_names = [column["name"] for column in columns]

        self.assertIn("TEST", column_names)


if __name__ == "__main__":
    unittest.main()
