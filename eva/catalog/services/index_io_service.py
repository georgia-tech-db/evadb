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

from eva.catalog.models.index_io import IndexIO
from eva.catalog.services.base_service import BaseService
from eva.utils.logging_manager import logger


class IndexIOService(BaseService):
    def __init__(self):
        super().__init__(IndexIO)

    def get_inputs_by_index_id(self, index_id: int):
        try:
            result = self.model.query.filter(
                self.model._index_id == index_id,
                self.model._is_input == True,  # noqa
            ).all()
            return result
        except Exception as e:
            error = f"Getting inputs for index id {index_id} raised {e}"
            logger.error(error)
            raise RuntimeError(error)

    def get_outputs_by_index_id(self, index_id: int):
        try:
            result = self.model.query.filter(
                self.model._index_id == index_id,
                self.model._is_input == False,  # noqa
            ).all()
            return result
        except Exception as e:
            error = f"Getting outputs for index id {index_id} raised {e}"
            logger.error(error)
            raise RuntimeError(error)

    def add_index_io(self, io_list: List[IndexIO]):
        for io in io_list:
            io.save()
