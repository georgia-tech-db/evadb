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
from datetime import datetime
from test.util import get_evadb_for_testing, shutdown_ray

from evadb.executor.executor_utils import ExecutorError
from evadb.server.command_handler import execute_query_fetch_all


class CreateJobTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        cls.evadb.catalog().reset()
        cls.job_name = "test_async_job"

    def setUp(self):
        execute_query_fetch_all(self.evadb, f"DROP JOB IF EXISTS {self.job_name};")

    @classmethod
    def tearDownClass(cls):
        shutdown_ray()
        execute_query_fetch_all(cls.evadb, f"DROP JOB IF EXISTS {cls.job_name};")

    def test_invalid_query_in_job_should_raise_exception(self):
        # missing closing paranthesis in the query
        query = f"""CREATE JOB {self.job_name} AS {{
                    CREATE OR REPLACE FUNCTION HomeSalesForecast FROM
                        ( SELECT * FROM postgres_data.home_sales
                    TYPE Forecasting
                    PREDICT 'price';
                }}
                START '2023-04-01 01:10:00'
                END '2023-05-01'
                EVERY 2 week;
            """
        with self.assertRaisesRegex(Exception, "Failed to parse the job query"):
            execute_query_fetch_all(self.evadb, query)

    def test_create_job_should_add_the_entry(self):
        queries = [
            """CREATE OR REPLACE FUNCTION HomeSalesForecast FROM
                ( SELECT * FROM postgres_data.home_sales )
                TYPE Forecasting
                PREDICT 'price';""",
            "Select HomeSalesForecast(10);",
        ]
        start = "2023-04-01 01:10:00"
        end = "2023-05-01"
        repeat_interval = 2
        repeat_period = "week"

        all_queries = "".join(queries)
        query = f"""CREATE JOB {self.job_name} AS {{
                   {all_queries}
                }}
                START '{start}'
                END '{end}'
                EVERY {repeat_interval} {repeat_period};"""

        execute_query_fetch_all(self.evadb, query)

        datetime_format = "%Y-%m-%d %H:%M:%S"
        date_format = "%Y-%m-%d"
        job_entry = self.evadb.catalog().get_job_catalog_entry(self.job_name)
        self.assertEqual(job_entry.name, self.job_name)
        self.assertEqual(
            job_entry.start_time, datetime.strptime(start, datetime_format)
        )
        self.assertEqual(job_entry.end_time, datetime.strptime(end, date_format))
        self.assertEqual(job_entry.repeat_interval, 2 * 7 * 24 * 60 * 60)
        self.assertEqual(job_entry.active, True)
        self.assertEqual(len(job_entry.queries), len(queries))

    def test_should_create_job_with_if_not_exists(self):
        if_not_exists = "IF NOT EXISTS"

        queries = [
            """CREATE OR REPLACE FUNCTION HomeSalesForecast FROM
                ( SELECT * FROM postgres_data.home_sales )
                TYPE Forecasting
                PREDICT 'price';""",
            "Select HomeSalesForecast(10);",
        ]

        query = """CREATE JOB {} {} AS {{
                    {}
                }}
                START '2023-04-01'
                END '2023-05-01'
                EVERY 2 week;
            """

        # Create the database.
        execute_query_fetch_all(
            self.evadb, query.format(if_not_exists, self.job_name, "".join(queries))
        )

        # Trying to create the same database should raise an exception.
        with self.assertRaises(ExecutorError):
            execute_query_fetch_all(
                self.evadb, query.format("", self.job_name, "".join(queries))
            )

        # Trying to create the same database should warn if "IF NOT EXISTS" is provided.
        execute_query_fetch_all(
            self.evadb, query.format(if_not_exists, self.job_name, "".join(queries))
        )


if __name__ == "__main__":
    unittest.main()
