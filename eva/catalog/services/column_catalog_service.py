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

from sqlalchemy.orm.exc import NoResultFound

from eva.catalog.models.column_catalog import ColumnCatalog
from eva.catalog.models.table_catalog import TableCatalog
from eva.catalog.services.base_service import BaseService


class ColumnCatalogService(BaseService):
    def __init__(self):
        super().__init__(ColumnCatalog)

    def filter_entry_by_table_id_and_name(self, table_id, column_name):
        try:
            return self.model.query.filter(
                self.model._table_id == table_id,
                self.model._name == column_name,
            ).one()
        except NoResultFound:
            return None

    def filter_entries_by_table_id(self, table_id: int):
        """return all the columns for table table_id

        Arguments:
            table_id {int} -- [table id of the table]

        Returns:
            List[self.model] -- [the filtered self.models]
        """
        return self.model.query.filter(self.model._table_id == table_id).all()

    def insert_entries(self, column_list):
        saved_column_list = []
        for column in column_list:
            saved_column_list.append(column.save())
        return saved_column_list

    def filter_entries_by_table(self, table: TableCatalog) -> List[ColumnCatalog]:
        try:
            return self.model.query.filter(self.model._table_id == table.id).all()
        except NoResultFound:
            return None
