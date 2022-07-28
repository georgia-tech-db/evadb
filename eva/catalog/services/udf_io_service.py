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

from eva.catalog.models.udf_io import UdfIO
from eva.catalog.services.base_service import BaseService
from eva.utils.logging_manager import logger


class UdfIOService(BaseService):
    def __init__(self):
        super().__init__(UdfIO)

    def get_inputs_by_udf_id(self, udf_id: int):
        try:
            result = self.model.query.filter(
                self.model._udf_id == udf_id,
                self.model._is_input == True,  # noqa
            ).all()
            return result
        except Exception as e:
            error = f"Getting inputs for UDF id {udf_id} raised {e}"
            logger.error(error)
            raise RuntimeError(error)

    def get_outputs_by_udf_id(self, udf_id: int):
        try:
            result = self.model.query.filter(
                self.model._udf_id == udf_id,
                self.model._is_input == False,  # noqa
            ).all()
            return result
        except Exception as e:
            error = f"Getting outputs for UDF id {udf_id} raised {e}"
            logger.error(error)
            raise RuntimeError(error)

    def add_udf_io(self, io_list: List[UdfIO]):
        """Commit an entry in the udf_io table

        Arguments:
            io_list (List[UdfIO]): List of io info io be added
        """

        for io in io_list:
            io.save()
