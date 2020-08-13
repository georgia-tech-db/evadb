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
from typing import List
from sqlalchemy.orm.exc import NoResultFound

from src.catalog.models.udf_io import UdfIO
from src.catalog.services.base_service import BaseService


class UdfIOService(BaseService):
    def __init__(self):
        super().__init__(UdfIO)

    def get_inputs_by_udf_id(self, udf_id: int):
        result = self.model.query \
            .with_entities(self.model._id) \
            .filter(self.model._udf_id == udf_id,
                    self.model._is_input == True).all()  # noqa

        return result

    def get_outputs_by_udf_id(self, udf_id: int):
        result = self.model.query \
            .with_entities(self.model._id) \
            .filter(self.model._udf_id == udf_id,
                    self.model._is_input == False).all()  # noqa

        return result

    def add_udf_io(self, io_list: List[UdfIO]):
        """Commit an entry in the udf_io table

        Arguments:
            io_list (List[UdfIO]): List of io info io be added
        """

        for io in io_list:
            io.save()

    def udf_io_by_name(self, name: str):
        """return the udf_io entry that matches the name provided.
           None if no such entry found.

        Arguments:
            name (str): name to be searched
        """

        try:
            return self.model.query.filter(self.model._name == name).one()
        except NoResultFound:
            return None
