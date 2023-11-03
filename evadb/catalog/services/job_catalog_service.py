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

from sqlalchemy import and_, true
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from evadb.catalog.models.job_catalog import JobCatalog
from evadb.catalog.models.utils import JobCatalogEntry
from evadb.catalog.services.base_service import BaseService
from evadb.utils.errors import CatalogError
from evadb.utils.logging_manager import logger


class JobCatalogService(BaseService):
    def __init__(self, db_session: Session):
        super().__init__(JobCatalog, db_session)

    def insert_entry(
        self,
        name: str,
        queries: list,
        start_time: datetime,
        end_time: datetime,
        repeat_interval: int,
        active: bool,
        next_schedule_run: datetime,
    ) -> JobCatalogEntry:
        try:
            job_catalog_obj = self.model(
                name=name,
                queries=json.dumps(queries),
                start_time=start_time,
                end_time=end_time,
                repeat_interval=repeat_interval,
                active=active,
                next_schedule_run=next_schedule_run,
            )
            job_catalog_obj = job_catalog_obj.save(self.session)

        except Exception as e:
            logger.exception(
                f"Failed to insert entry into job catalog with exception {str(e)}"
            )
            raise CatalogError(e)

        return job_catalog_obj.as_dataclass()

    def get_entry_by_name(self, job_name: str) -> JobCatalogEntry:
        """
        Get the job catalog entry with given job name.
        Arguments:
            job_name  (str): Job name
        Returns:
            JobCatalogEntry - catalog entry for given job name
        """
        entry = self.session.execute(
            select(self.model).filter(self.model._name == job_name)
        ).scalar_one_or_none()
        if entry:
            return entry.as_dataclass()
        return entry

    def delete_entry(self, job_entry: JobCatalogEntry):
        """Delete Job from the catalog
        Arguments:
            job  (JobCatalogEntry): job to delete
        Returns:
            True if successfully removed else false
        """
        try:
            job_catalog_obj = self.session.execute(
                select(self.model).filter(self.model._row_id == job_entry.row_id)
            ).scalar_one_or_none()
            job_catalog_obj.delete(self.session)
            return True
        except Exception as e:
            err_msg = f"Delete Job failed for {job_entry} with error {str(e)}."
            logger.exception(err_msg)
            raise CatalogError(err_msg)

    def get_all_overdue_jobs(self) -> list:
        """Get the list of jobs that are overdue to be triggered
        Arguments:
            None
        Returns:
            Returns the list of all active overdue jobs
        """
        entries = (
            self.session.execute(
                select(self.model).filter(
                    and_(
                        self.model._next_scheduled_run <= datetime.datetime.now(),
                        self.model._active == true(),
                    )
                )
            )
            .scalars()
            .all()
        )
        entries = [row.as_dataclass() for row in entries]
        return entries

    def get_next_executable_job(self, only_past_jobs: bool) -> JobCatalogEntry:
        """Get the oldest job that is ready to be triggered by trigger time
        Arguments:
            only_past_jobs (bool): boolean flag to denote if only jobs with trigger time in
                past should be considered
        Returns:
            Returns the first job to be triggered
        """
        entry = self.session.execute(
            select(self.model)
            .filter(
                and_(
                    self.model._next_scheduled_run <= datetime.datetime.now(),
                    self.model._active == true(),
                )
                if only_past_jobs
                else self.model._active == true()
            )
            .order_by(self.model._next_scheduled_run.asc())
            .limit(1)
        ).scalar_one_or_none()
        if entry:
            return entry.as_dataclass()
        return entry

    def update_next_scheduled_run(
        self, job_name: str, next_scheduled_run: datetime, active: bool
    ):
        """Update the next_scheduled_run and active column as per the provided values
        Arguments:
            job_name (str): job which should be updated

            next_run_time (datetime): the next trigger time for the job

            active (bool): the active status for the job
        Returns:
            void
        """
        job = (
            self.session.query(self.model).filter(self.model._name == job_name).first()
        )
        if job:
            job._next_scheduled_run = next_scheduled_run
            job._active = active
            self.session.commit()
