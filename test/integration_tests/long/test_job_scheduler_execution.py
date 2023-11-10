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
import time
import unittest
from datetime import datetime, timedelta
from test.util import get_evadb_for_testing, shutdown_ray

from mock import MagicMock

from evadb.interfaces.relational.db import EvaDBConnection
from evadb.server.command_handler import execute_query_fetch_all


class JobSchedulerIntegrationTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        cls.evadb.catalog().reset()
        cls.job_name_1 = "test_async_job_1"
        cls.job_name_2 = "test_async_job_2"

    def setUp(self):
        execute_query_fetch_all(self.evadb, f"DROP JOB IF EXISTS {self.job_name_1};")
        execute_query_fetch_all(self.evadb, f"DROP JOB IF EXISTS {self.job_name_2};")

    @classmethod
    def tearDownClass(cls):
        shutdown_ray()
        execute_query_fetch_all(cls.evadb, f"DROP JOB IF EXISTS {cls.job_name_1};")
        execute_query_fetch_all(cls.evadb, f"DROP JOB IF EXISTS {cls.job_name_2};")

    def create_jobs(self):
        datetime_format = "%Y-%m-%d %H:%M:%S"
        start_time = (datetime.now() - timedelta(seconds=10)).strftime(datetime_format)
        end_time = (datetime.now() + timedelta(seconds=60)).strftime(datetime_format)

        create_csv_query = """CREATE TABLE IF NOT EXISTS MyCSV (
                                    id INTEGER UNIQUE,
                                    frame_id INTEGER,
                                    video_id INTEGER
                                );
                            """
        job_1_query = f"""CREATE JOB IF NOT EXISTS {self.job_name_1} AS {{
                                SELECT * FROM MyCSV;
                            }}
                            START '{start_time}'
                            END '{end_time}'
                            EVERY 4 seconds;
                        """
        job_2_query = f"""CREATE JOB IF NOT EXISTS {self.job_name_2} AS {{
                            SHOW FUNCTIONS;
                        }}
                        START '{start_time}'
                        END '{end_time}'
                        EVERY 2 seconds;
                    """

        execute_query_fetch_all(self.evadb, create_csv_query)
        execute_query_fetch_all(self.evadb, job_1_query)
        execute_query_fetch_all(self.evadb, job_2_query)

    def test_should_execute_the_scheduled_jobs(self):
        self.create_jobs()
        connection = EvaDBConnection(self.evadb, MagicMock(), MagicMock())

        # start the job scheduler
        connection.start_jobs()

        # let the job scheduler run for 10 seconds
        time.sleep(15)
        connection.stop_jobs()

        job_1_execution_count = len(self.evadb.catalog().get_job_history_by_job_id(1))
        job_2_execution_count = len(self.evadb.catalog().get_job_history_by_job_id(2))

        self.assertGreater(job_2_execution_count, job_1_execution_count)
        self.assertGreater(job_2_execution_count, 2)
        self.assertGreater(job_1_execution_count, 2)
