# coding=utf-8
# Copyright 2018-2022 EVA
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

from eva.catalog.models.udf_io_catalog import UdfIOCatalog, UdfIOCatalogEntry
from eva.catalog.services.base_service import BaseService
from eva.utils.logging_manager import logger


class UdfIOCatalogService(BaseService):
    def __init__(self):
        super().__init__(UdfIOCatalog)

    def get_input_entries_by_udf_id(self, udf_id: int) -> List[UdfIOCatalogEntry]:
        try:
            result = self.model.query.filter(
                self.model._udf_id == udf_id,
                self.model._is_input == True,  # noqa
            ).all()
            return [obj.as_dataclass() for obj in result]
        except Exception as e:
            error = f"Getting inputs for UDF id {udf_id} raised {e}"
            logger.error(error)
            raise RuntimeError(error)

    def get_output_entries_by_udf_id(self, udf_id: int) -> List[UdfIOCatalogEntry]:
        try:
            result = self.model.query.filter(
                self.model._udf_id == udf_id,
                self.model._is_input == False,  # noqa
            ).all()
            return [obj.as_dataclass() for obj in result]
        except Exception as e:
            error = f"Getting outputs for UDF id {udf_id} raised {e}"
            logger.error(error)
            raise RuntimeError(error)

    def insert_entries(self, io_list: List[UdfIOCatalogEntry]):
        """Commit entries to the udf_io table

        Arguments:
            io_list (List[UdfIOCatalogEntry]): List of io info io be added
        """

        for io in io_list:
            io_obj = UdfIOCatalog(
                name=io.name,
                type=io.type,
                is_nullable=io.is_nullable,
                array_type=io.array_type,
                array_dimensions=io.array_dimensions,
                is_input=io.is_input,
                udf_id=io.udf_id,
            )
            io_obj.save()
