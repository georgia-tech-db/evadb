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

from eva.catalog.models.udf_history_column import UdfHistoryColumn
from eva.catalog.services.base_service import BaseService
from eva.utils.logging_manager import logger


class UdfHistoryColumnService(BaseService):
    def __init__(self):
        super().__init__(UdfHistoryColumn)

    def get_cols_by_udf_history_id(self, udf_history_id: int) -> List[int]:
        """Return all columns of given udf history.

        Arguments:
            udf_history_id (int): id of udf history to be matched

        Returns:
            List of columns (foreign key of df_column) order by arg_index
        """
        result = (
            self.model.query.with_entities(self.model._arg)
            .filter(self.model._udf_history_id == udf_history_id)
            .order_by(self.model._arg_index)
            .all()
        )
        return result

    def create_udf_history_cols(self, udf_history_id: int, cols: List[int]) -> bool:
        """Create udf history columns for one udf history entry

        Arguments:
            udf_history_id (int): id of udf history
            cols (List[int]): id of cols (foreign key of df_column) in order

        Returns:
            True if successfully created else False
        """
        udf_history_columns = []
        try:
            for idx, arg in enumerate(cols):
                udf_history_columns.append(UdfHistoryColumn(udf_history_id, arg, idx))
            for col in udf_history_columns:
                col.save()
        except Exception as e:
            logger.error("Creating udf history columns failed with {}".format(e))
            return False
        return True
