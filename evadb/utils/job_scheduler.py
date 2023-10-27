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
import time
import sys

from evadb.catalog.models.utils import JobCatalogEntry
from evadb.database import EvaDBDatabase
from evadb.server.command_handler import execute_query
from evadb.utils.generic_utils import parse_config_yml
from evadb.utils.logging_manager import logger

class JobScheduler:
    # read jobs with next trigger in the past
    # execute the task with oldest trigger date
    # update the next trigger date and TODO: update job history in one transaction
    # sleep till next wakeup time

    def __init__(self, evadb: EvaDBDatabase) -> None:
        config_object = parse_config_yml()
        self.jobs_config = config_object["jobs"] if config_object is not None else {"poll_interval": 30}
        self._evadb = evadb

    def _update_next_schedule_run(self, job_catalog_entry: JobCatalogEntry) -> bool:
        job_end_time = job_catalog_entry.end_time
        active_status = False
        if job_catalog_entry.repeat_interval > 0:
            next_trigger_time = datetime.datetime.now() + datetime.timedelta(seconds=job_catalog_entry.repeat_interval)
            if next_trigger_time < job_end_time:
                active_status = True

        self._evadb.catalog().update_job_catalog_entry(
            job_catalog_entry.name,
            next_trigger_time if active_status else job_catalog_entry.next_scheduled_run,
            active_status
        )
        return active_status

    def _scan_and_execute_jobs(self):
        while True:
            try:
                for next_executable_job in iter(lambda: self._evadb.catalog().get_next_executable_job(only_past_jobs=True), None):
                    execution_results = [execute_query(self._evadb, query) for query in next_executable_job.queries]
                    self._update_next_schedule_run(next_executable_job)

                next_executable_job = self._evadb.catalog().get_next_executable_job(only_past_jobs=False)
                if next_executable_job.next_scheduled_run > datetime.datetime.now():
                    sleep_time = min(
                        self.jobs_config["poll_interval"],
                        (next_executable_job.next_scheduled_run - datetime.datetime.now()).total_seconds()
                    )
                    logger.debug(f"Job scheduler process sleeping for {sleep_time} seconds")
                    time.sleep(sleep_time)
            except Exception as e:
                logger.error(f"Got an exception in job scheduler: {str(e)}")
                time.sleep(self.jobs_config["poll_interval"] * 0.2)

    def execute(self):
        try:
            self._scan_and_execute_jobs()
        except KeyboardInterrupt:
            logger.debug("Exiting the job scheduler process due to interrupt")
            sys.exit()