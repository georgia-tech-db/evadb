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
from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from evadb.catalog.models.job_history_catalog import JobHistoryCatalog
from evadb.catalog.models.utils import JobHistoryCatalogEntry
from evadb.catalog.services.base_service import BaseService
from evadb.utils.errors import CatalogError
from evadb.utils.logging_manager import logger


class JobHistoryCatalogService(BaseService):
    def __init__(self, db_session: Session):
        super().__init__(JobHistoryCatalog, db_session)

    def insert_entry(
        self,
        job_id: str,
        job_name: str,
        execution_start_time: datetime,
        execution_end_time: datetime,
    ) -> JobHistoryCatalogEntry:
        try:
            job_history_catalog_obj = self.model(
                job_id=job_id,
                job_name=job_name,
                execution_start_time=execution_start_time,
                execution_end_time=execution_end_time,
            )
            job_history_catalog_obj = job_history_catalog_obj.save(self.session)

        except Exception as e:
            logger.exception(
                f"Failed to insert entry into job history catalog with exception {str(e)}"
            )
            raise CatalogError(e)

        return job_history_catalog_obj.as_dataclass()

    def get_entry_by_job_id(self, job_id: int) -> List[JobHistoryCatalogEntry]:
        """
        Get all the job history catalog entry with given job id.
        Arguments:
            job_id (int): Job id
        Returns:
            list[JobHistoryCatalogEntry]: all history catalog entries for given job id
        """
        entries = (
            self.session.execute(
                select(self.model).filter(self.model._job_id == job_id)
            )
            .scalars()
            .all()
        )
        entries = [row.as_dataclass() for row in entries]
        return entries

    def update_entry_end_time(
        self, job_id: int, execution_start_time: datetime, execution_end_time: datetime
    ):
        """Update the execution_end_time of the entry as per the provided values
        Arguments:
            job_id (int): id of the job whose history entry which should be updated

            execution_start_time (datetime): the start time for the job history entry

            execution_end_time (datetime): the end time for the job history entry
        Returns:
            void
        """
        job_history_entry = (
            self.session.query(self.model)
            .filter(
                and_(
                    self.model._job_id == job_id,
                    self.model._execution_start_time == execution_start_time,
                )
            )
            .first()
        )
        if job_history_entry:
            job_history_entry._execution_end_time = execution_end_time
            self.session.commit()
