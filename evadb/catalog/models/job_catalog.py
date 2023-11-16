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
import json

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String
from sqlalchemy.orm import relationship

from evadb.catalog.models.base_model import BaseModel
from evadb.catalog.models.utils import JobCatalogEntry


class JobCatalog(BaseModel):
    """The `JobCatalog` catalog stores information about all the created Jobs.
    `_row_id:` an autogenerated unique identifier.
    `_name:` the job name.
    `_queries:` the queries to run as part of this job
    `_start_time:` the job's start time
    `_end_time:` the job's end time
    `_repeat_interval:` the job's repeat interval
    `_repeat_period:` the job's repeat period
    `_active:` is the job active/deleted
    `_next_scheduled_run:` the next trigger time for the job as per the schedule
    `_created_at:` entry creation time
    `_updated_at:` entry last update time
    """

    __tablename__ = "job_catalog"

    _name = Column("name", String(100), unique=True)
    _queries = Column("queries", String, nullable=False)
    _start_time = Column("start_time", DateTime, default=datetime.datetime.now)
    _end_time = Column("end_ts", DateTime)
    _repeat_interval = Column("repeat_interval", Integer)
    _active = Column("active", Boolean, default=True)
    _next_scheduled_run = Column("next_scheduled_run", DateTime)

    _created_at = Column("created_at", DateTime, default=datetime.datetime.now)
    _updated_at = Column(
        "updated_at",
        DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    )

    _next_run_index = Index("_next_run_index", _next_scheduled_run)
    _job_history_catalog = relationship("JobHistoryCatalog", cascade="all, delete")

    def __init__(
        self,
        name: str,
        queries: str,
        start_time: datetime,
        end_time: datetime,
        repeat_interval: Integer,
        active: bool,
        next_schedule_run: datetime,
    ):
        self._name = name
        self._queries = queries
        self._start_time = start_time
        self._end_time = end_time
        self._repeat_interval = repeat_interval
        self._active = active
        self._next_scheduled_run = next_schedule_run

    def as_dataclass(self) -> "JobCatalogEntry":
        return JobCatalogEntry(
            row_id=self._row_id,
            name=self._name,
            queries=json.loads(self._queries),
            start_time=self._start_time,
            end_time=self._end_time,
            repeat_interval=self._repeat_interval,
            active=self._active,
            next_scheduled_run=self._next_scheduled_run,
            created_at=self._created_at,
            updated_at=self._updated_at,
        )
