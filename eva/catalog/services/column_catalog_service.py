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

from eva.catalog.models.column_catalog import ColumnCatalog, ColumnCatalogEntry
from eva.catalog.models.table_catalog import TableCatalog, TableCatalogEntry
from eva.catalog.services.base_service import BaseService


class ColumnCatalogService(BaseService):
    def __init__(self):
        super().__init__(ColumnCatalog)

    @classmethod
    def _column_catalog_object_to_column_catalog_entry(cls, obj: ColumnCatalog):
        if obj is None:
            return None
        return ColumnCatalogEntry(
            id=obj.id,
            name=obj.name,
            type=obj.type,
            is_nullable=obj.is_nullable,
            array_type=obj.array_type,
            array_dimensions=obj.array_dimensions,
            table_id=obj.table_id,
        )

    @classmethod
    def _column_catalog_entry_to_column_catalog_object(cls, obj: ColumnCatalogEntry):
        if obj is None:
            return None
        return ColumnCatalog(
            name=obj.name,
            type=obj.type,
            is_nullable=obj.is_nullable,
            array_type=obj.array_type,
            array_dimensions=obj.array_dimensions,
            table_id=obj.table_id,
        )

    def filter_entry_by_table_id_and_name(self, table_id, column_name):
        entry = self.model.query.filter(
            self.model._table_id == table_id,
            self.model._name == column_name,
        ).one_or_none()
        return self._column_catalog_object_to_column_catalog_entry(entry)

    def filter_entries_by_table_id(self, table_id: int):
        """return all the columns for table table_id

        Arguments:
            table_id {int} -- [table id of the table]

        Returns:
            List[self.model] -- [the filtered self.models]
        """
        entries = self.model.query.filter(self.model._table_id == table_id).all()
        return [
            self._column_catalog_object_to_column_catalog_entry(entry)
            for entry in entries
        ]

    def insert_entries(self, column_list: List[ColumnCatalogEntry]):
        catalog_column_objs = [
            self._column_catalog_entry_to_column_catalog_object(entry)
            for entry in column_list
        ]
        saved_column_objs = []
        for column in catalog_column_objs:
            saved_column_objs.append(column.save())
        return [
            self._column_catalog_object_to_column_catalog_entry(obj)
            for obj in saved_column_objs
        ]

    def filter_entries_by_table(
        self, table: TableCatalogEntry
    ) -> List[ColumnCatalogEntry]:
        try:
            entries = self.model.query.filter(self.model._table_id == table.id).all()
            return [
                self._column_catalog_object_to_column_catalog_entry(entry)
                for entry in entries
            ]
        except NoResultFound:
            return None
