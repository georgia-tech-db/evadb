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
import re
from datetime import datetime

import pandas as pd

from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.executor.executor_utils import ExecutorError
from evadb.models.storage.batch import Batch
from evadb.parser.create_statement import CreateJobStatement
from evadb.parser.parser import Parser
from evadb.utils.logging_manager import logger


class CreateJobExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: CreateJobStatement):
        super().__init__(db, node)

    def _parse_datetime_str(self, datetime_str: str) -> datetime:
        datetime_format = "%Y-%m-%d %H:%M:%S"
        date_format = "%Y-%m-%d"

        if re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", datetime_str):
            try:
                return datetime.strptime(datetime_str, datetime_format)
            except ValueError:
                raise ExecutorError(
                    f"{datetime_str} is not in the correct datetime format. expected format: {datetime_format}."
                )
        elif re.match(r"\d{4}-\d{2}-\d{2}", datetime_str):
            try:
                return datetime.strptime(datetime_str, date_format)
            except ValueError:
                raise ExecutorError(
                    f"{datetime_str} is not in the correct date format. expected format: {date_format}."
                )
        else:
            raise ValueError(
                f"{datetime_str} does not match the expected date or datetime format"
            )

    def _get_repeat_time_interval_seconds(
        self, repeat_interval: int, repeat_period: str
    ) -> int:
        unit_to_seconds = {
            "seconds": 1,
            "minute": 60,
            "minutes": 60,
            "min": 60,
            "hour": 3600,
            "hours": 3600,
            "day": 86400,
            "days": 86400,
            "week": 604800,
            "weeks": 604800,
            "month": 2592000,
            "months": 2592000,
        }
        assert (repeat_period is None) or (
            repeat_period in unit_to_seconds
        ), "repeat period should be one of these values: seconds | minute | minutes | min | hour | hours | day | days | week | weeks | month | months"

        repeat_interval = 1 if repeat_interval is None else repeat_interval
        return repeat_interval * unit_to_seconds.get(repeat_period, 0)

    def exec(self, *args, **kwargs):
        # Check if the job already exists.
        job_catalog_entry = self.catalog().get_job_catalog_entry(self.node.job_name)

        if job_catalog_entry is not None:
            if self.node.if_not_exists:
                msg = f"A job with name {self.node.job_name} already exists, nothing added."
                yield Batch(pd.DataFrame([msg]))
                return
            else:
                raise ExecutorError(
                    f"A job with name {self.node.job_name} already exists."
                )

        logger.debug(f"Creating job {self.node}")

        job_name = self.node.job_name
        queries = []
        parser = Parser()

        for q in self.node.queries:
            try:
                curr_query = str(q)
                parser.parse(curr_query)
                queries.append(curr_query)
            except Exception:
                error_msg = f"Failed to parse the job query: {curr_query}"
                logger.exception(error_msg)
                raise ExecutorError(error_msg)
        start_time = (
            self._parse_datetime_str(self.node.start_time)
            if self.node.start_time is not None
            else datetime.datetime.now()
        )
        end_time = (
            self._parse_datetime_str(self.node.end_time)
            if self.node.end_time is not None
            else None
        )
        repeat_interval = self._get_repeat_time_interval_seconds(
            self.node.repeat_interval, self.node.repeat_period
        )
        active = True
        next_schedule_run = start_time

        self.catalog().insert_job_catalog_entry(
            job_name,
            queries,
            start_time,
            end_time,
            repeat_interval,
            active,
            next_schedule_run,
        )

        yield Batch(
            pd.DataFrame(
                [f"The job {self.node.job_name} has been successfully created."]
            )
        )
