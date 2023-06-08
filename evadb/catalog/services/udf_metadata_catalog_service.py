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
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from evadb.catalog.models.udf_metadata_catalog import (
    UdfMetadataCatalog,
    UdfMetadataCatalogEntry,
)
from evadb.catalog.services.base_service import BaseService
from evadb.utils.errors import CatalogError
from evadb.utils.logging_manager import logger


class UdfMetadataCatalogService(BaseService):
    def __init__(self, db_session: Session):
        super().__init__(UdfMetadataCatalog, db_session)

    def insert_entries(self, entries: List[UdfMetadataCatalogEntry]):
        try:
            for entry in entries:
                metadata_obj = UdfMetadataCatalog(
                    key=entry.key, value=entry.value, udf_id=entry.udf_id
                )
                metadata_obj.save(self.session)
        except Exception as e:
            logger.exception(
                f"Failed to insert entry {entry} into udf metadata catalog with exception {str(e)}"
            )
            raise CatalogError(e)

    def get_entries_by_udf_id(self, udf_id: int) -> List[UdfMetadataCatalogEntry]:
        try:
            result = (
                self.session.execute(
                    select(self.model).filter(
                        self.model._udf_id == udf_id,
                    )
                )
                .scalars()
                .all()
            )
            return [obj.as_dataclass() for obj in result]
        except Exception as e:
            error = f"Getting metadata entries for UDF id {udf_id} raised {e}"
            logger.error(error)
            raise CatalogError(error)
