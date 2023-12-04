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

import multiprocessing

from evadb.database import EvaDBDatabase
from evadb.utils.job_scheduler import JobScheduler
from evadb.utils.logging_manager import logger

def start_jobs_process(db: EvaDBDatabase) -> multiprocessing.Process:
    """
    Initializes the jobs process and returns a multiprocessing.Process object
    """
    job_scheduler = JobScheduler(db)
    _jobs_process = multiprocessing.Process(target=job_scheduler.execute)
    _jobs_process.daemon = True
    _jobs_process.start()
    logger.debug("Job scheduler process started")
    print("Job scheduler process started")
    return _jobs_process
