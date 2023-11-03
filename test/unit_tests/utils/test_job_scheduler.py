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
from datetime import datetime, timedelta

from mock import MagicMock

from evadb.catalog.models.utils import JobCatalogEntry
from evadb.utils.job_scheduler import JobScheduler


class JobSchedulerTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_dummy_job_catalog_entry(self, active, job_name, next_run):
        return JobCatalogEntry(
            name=job_name,
            queries=None,
            start_time=None,
            end_time=None,
            repeat_interval=None,
            active=active,
            next_scheduled_run=next_run,
            created_at=None,
            updated_at=None,
        )

    def test_sleep_time_calculation(self):
        past_job = self.get_dummy_job_catalog_entry(
            True, "past_job", datetime.now() - timedelta(seconds=10)
        )
        future_job = self.get_dummy_job_catalog_entry(
            True, "future_job", datetime.now() + timedelta(seconds=20)
        )

        job_scheduler = JobScheduler(MagicMock())

        self.assertEqual(job_scheduler._get_sleep_time(past_job), 0)
        self.assertGreaterEqual(job_scheduler._get_sleep_time(future_job), 10)
        self.assertEqual(job_scheduler._get_sleep_time(None), 30)

    def test_update_next_schedule_run(self):
        future_time = datetime.now() + timedelta(seconds=1000)
        job_scheduler = JobScheduler(MagicMock())
        job_entry = self.get_dummy_job_catalog_entry(True, "job", datetime.now())

        # job which runs just once
        job_entry.end_time = future_time
        status, next_run = job_scheduler._update_next_schedule_run(job_entry)
        self.assertEqual(status, False, "status for one time job should be false")

        # recurring job with valid end date
        job_entry.end_time = future_time
        job_entry.repeat_interval = 120
        expected_next_run = datetime.now() + timedelta(seconds=120)
        status, next_run = job_scheduler._update_next_schedule_run(job_entry)
        self.assertEqual(status, True, "status for recurring time job should be true")
        self.assertGreaterEqual(next_run, expected_next_run)

        # recurring job with expired end date
        job_entry.end_time = datetime.now() + timedelta(seconds=60)
        job_entry.repeat_interval = 120
        expected_next_run = datetime.now() + timedelta(seconds=120)
        status, next_run = job_scheduler._update_next_schedule_run(job_entry)
        self.assertEqual(
            status, False, "status for rexpired ecurring time job should be false"
        )
        self.assertLessEqual(next_run, datetime.now())
