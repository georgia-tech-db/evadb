# coding=utf-8
# Copyright 2018-2020 EVA
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
from typing import Optional, List

from eva.catalog.models.udf_history import UdfHistory
from eva.catalog.services.base_service import BaseService
from sqlalchemy.orm.exc import NoResultFound

from eva.utils.logging_manager import logger


class UdfHistoryService(BaseService):
    def __init__(self):
        super().__init__(UdfHistory)

    def create_udf_history(self, udf_id: int, predicate: str,
                           materialize_view: str) -> UdfHistory:
        """Creates a new udf history entry

        Arguments:
            udf_id (int): id of the udf from UdfMetadata
            predicate (str): serialized sympy predicate
            materialize_view (str): the materialized table

        Returns:
            UdfHistory: Returns the new entry created
        """
        history = self.model(udf_id, predicate, materialize_view)
        history = history.save()
        return history

    def udf_history_by_id(self, id: int) -> Optional[UdfHistory]:
        """Return the udf history entry that matches the id provided.

        Arguments:
            id (int): id to be searched

        Returns:
           UdfHistory, None if no such entry found.
        """

        try:
            return self.model.query.filter(self.model._id == id).one()
        except NoResultFound:
            return None

    def udf_history_by_udfid(self, udf_id: int) -> List[UdfHistory]:
        """Return all udf history entries that matches the udf_id provided.

        Arguments:
            udf_id (id): id of udf from UdfMetadata

        Returns:
            List of udf history entries
        """

        result = self.model.query.filter(
            self.model._udf_id == udf_id
        ).all()
        return result




