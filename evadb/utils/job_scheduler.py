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

import datetime
import sys
import time

from evadb.catalog.models.utils import JobCatalogEntry
from evadb.database import EvaDBDatabase
from evadb.server.command_handler import execute_query
from evadb.utils.logging_manager import logger


class JobScheduler:
    def __init__(self, evadb: EvaDBDatabase) -> None:
        self.poll_interval_seconds = 30
        self._evadb = evadb

    def _update_next_schedule_run(self, job_catalog_entry: JobCatalogEntry) -> bool:
        job_end_time = job_catalog_entry.end_time
        active_status = False
        if job_catalog_entry.repeat_interval and job_catalog_entry.repeat_interval > 0:
            next_trigger_time = datetime.datetime.now() + datetime.timedelta(
                seconds=job_catalog_entry.repeat_interval
            )
            if not job_end_time or next_trigger_time < job_end_time:
                active_status = True

        next_trigger_time = (
            next_trigger_time if active_status else job_catalog_entry.next_scheduled_run
        )
        self._evadb.catalog().update_job_catalog_entry(
            job_catalog_entry.name,
            next_trigger_time,
            active_status,
        )
        return active_status, next_trigger_time

    def _get_sleep_time(self, next_job_entry: JobCatalogEntry) -> int:
        sleep_time = self.poll_interval_seconds
        if next_job_entry:
            sleep_time = min(
                sleep_time,
                (
                    next_job_entry.next_scheduled_run - datetime.datetime.now()
                ).total_seconds(),
            )
        sleep_time = max(0, sleep_time)
        return sleep_time

    def _scan_and_execute_jobs(self):
        while True:
            try:
                for next_executable_job in iter(
                    lambda: self._evadb.catalog().get_next_executable_job(
                        only_past_jobs=True
                    ),
                    None,
                ):
                    execution_time = datetime.datetime.now()

                    # insert a job history record to mark start of this execution
                    self._evadb.catalog().insert_job_history_catalog_entry(
                        next_executable_job.row_id,
                        next_executable_job.name,
                        execution_time,
                        None,
                    )

                    # execute the queries of the job
                    execution_results = [
                        execute_query(self._evadb, query)
                        for query in next_executable_job.queries
                    ]
                    logger.debug(
                        f"Exection result for job: {next_executable_job.name} results: {execution_results}"
                    )

                    # update the next trigger time for this job
                    self._update_next_schedule_run(next_executable_job)

                    # update the previosly inserted job history record with endtime
                    self._evadb.catalog().update_job_history_end_time(
                        next_executable_job.row_id,
                        execution_time,
                        datetime.datetime.now(),
                    )

                next_executable_job = self._evadb.catalog().get_next_executable_job(
                    only_past_jobs=False
                )

                sleep_time = self._get_sleep_time(next_executable_job)
                if sleep_time > 0:
                    logger.debug(
                        f"Job scheduler process sleeping for {sleep_time} seconds"
                    )
                    time.sleep(sleep_time)
            except Exception as e:
                logger.error(f"Got an exception in job scheduler: {str(e)}")
                time.sleep(self.poll_interval_seconds * 0.2)

    def execute(self):
        try:
            self._scan_and_execute_jobs()
        except KeyboardInterrupt:
            logger.debug("Exiting the job scheduler process due to interrupt")
            sys.exit()
