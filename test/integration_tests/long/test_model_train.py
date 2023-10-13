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
from test.markers import ludwig_skip_marker, sklearn_skip_marker, xgboost_skip_marker
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
        execute_query_fetch_all(
            cls.evadb, "DROP FUNCTION IF EXISTS PredictHouseRentLudwig;"
        )
        execute_query_fetch_all(
            cls.evadb, "DROP FUNCTION IF EXISTS PredictHouseRentSklearn;"
        )

    @ludwig_skip_marker
    def test_ludwig_automl(self):
        create_predict_function = """
            CREATE OR REPLACE FUNCTION PredictHouseRentLudwig FROM
            ( SELECT * FROM HomeRentals )
            TYPE Ludwig
            PREDICT 'rental_price'
            TIME_LIMIT 120;
        """
        execute_query_fetch_all(self.evadb, create_predict_function)

        predict_query = """
            SELECT PredictHouseRentLudwig(*) FROM HomeRentals LIMIT 10;
        """
        result = execute_query_fetch_all(self.evadb, predict_query)
        self.assertEqual(len(result.columns), 1)
        self.assertEqual(len(result), 10)

    @sklearn_skip_marker
    def test_sklearn_regression(self):
        create_predict_function = """
            CREATE OR REPLACE FUNCTION PredictHouseRentSklearn FROM
            ( SELECT number_of_rooms, number_of_bathrooms, days_on_market, rental_price FROM HomeRentals )
            TYPE Sklearn
            PREDICT 'rental_price';
        """
        execute_query_fetch_all(self.evadb, create_predict_function)

        predict_query = """
            SELECT PredictHouseRentSklearn(number_of_rooms, number_of_bathrooms, days_on_market, rental_price) FROM HomeRentals LIMIT 10;
        """
        result = execute_query_fetch_all(self.evadb, predict_query)
        self.assertEqual(len(result.columns), 1)
        self.assertEqual(len(result), 10)

    @xgboost_skip_marker
    def test_xgboost_regression(self):
        create_predict_function = """
            CREATE FUNCTION IF NOT EXISTS PredictRent FROM
            ( SELECT number_of_rooms, number_of_bathrooms, days_on_market, rental_price FROM HomeRentals )
            TYPE XGBoost
            PREDICT 'rental_price'
            TIME_LIMIT 180
            METRIC 'r2';
        """
        execute_query_fetch_all(self.evadb, create_predict_function)

        predict_query = """
            SELECT PredictRent(number_of_rooms, number_of_bathrooms, days_on_market, rental_price) FROM HomeRentals LIMIT 10;
        """
        result = execute_query_fetch_all(self.evadb, predict_query)
        self.assertEqual(len(result.columns), 1)
        self.assertEqual(len(result), 10)


if __name__ == "__main__":
    unittest.main()
