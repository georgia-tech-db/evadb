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
from test.markers import ludwig_skip_marker
from test.util import get_evadb_for_testing, shutdown_ray

import pytest

from evadb.configuration.constants import EvaDB_ROOT_DIR
from evadb.server.command_handler import execute_query_fetch_all


@pytest.mark.notparallel
class ModelTrainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        cls.evadb.catalog().reset()

        create_table_query = """
           CREATE TABLE IF NOT EXISTS HomeRentals (
               number_of_rooms INTEGER,
               number_of_bathrooms INTEGER,
               sqft INTEGER,
               location TEXT(128),
               days_on_market INTEGER,
               initial_price INTEGER,
               neighborhood TEXT(128),
               rental_price FLOAT(64,64)
           );"""
        execute_query_fetch_all(cls.evadb, create_table_query)

        path = f"{EvaDB_ROOT_DIR}/data/ludwig/home_rentals.csv"
        load_query = f"LOAD CSV '{path}' INTO HomeRentals;"
        execute_query_fetch_all(cls.evadb, load_query)

    @classmethod
    def tearDownClass(cls):
        shutdown_ray()

        # clean up
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS HomeRentals;")

    @ludwig_skip_marker
    def test_ludwig_automl(self):
        create_predict_udf = """
            CREATE UDF IF NOT EXISTS PredictHouseRent FROM
            ( SELECT * FROM HomeRentals )
            TYPE Ludwig
            'predict' 'rental_price'
            'time_limit' 120;
        """
        execute_query_fetch_all(self.evadb, create_predict_udf)

        predict_query = """
            SELECT PredictHouseRent(*) FROM HomeRentals LIMIT 10;
        """
        result = execute_query_fetch_all(self.evadb, predict_query)
        self.assertEqual(len(result.columns), 1)
        self.assertEqual(len(result), 10)


if __name__ == "__main__":
    unittest.main()
