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
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import select

from evadb.catalog.models.column_catalog import ColumnCatalog
from evadb.catalog.models.utils import ColumnCatalogEntry, TableCatalogEntry
from evadb.catalog.services.base_service import BaseService


class ColumnCatalogService(BaseService):
    def __init__(self, db_session: Session):
        super().__init__(ColumnCatalog, db_session)

    def filter_entry_by_table_id_and_name(
        self, table_id, column_name
    ) -> ColumnCatalogEntry:
        entry = self.session.execute(
            select(self.model).filter(
                self.model._table_id == table_id,
                self.model._name == column_name,
            )
        ).scalar_one_or_none()
        if entry:
            return entry.as_dataclass()
        return entry

    def filter_entries_by_table_id(self, table_id: int) -> List[ColumnCatalogEntry]:
        """return all the columns for table table_id"""
        entries = (
            self.session.execute(
                select(self.model).filter(
                    self.model._table_id == table_id,
                )
            )
            .scalars()
            .all()
        )
        return [entry.as_dataclass() for entry in entries]

    def get_entry_by_id(
        self, col_id: int, return_alchemy=False
    ) -> List[ColumnCatalogEntry]:
        entry = self.session.execute(
            select(self.model).filter(self.model._row_id == col_id)
        ).scalar_one_or_none()
        if entry:
            return entry if return_alchemy else entry.as_dataclass()
        return entry

    def insert_entries(self, column_list: List[ColumnCatalogEntry]):
        catalog_column_objs = [
            self.model(
                name=col.name,
                type=col.type,
                is_nullable=col.is_nullable,
                array_type=col.array_type,
                array_dimensions=col.array_dimensions,
                table_id=col.table_id,
            )
            for col in column_list
        ]
        saved_column_objs = []
        for column in catalog_column_objs:
            saved_column_objs.append(column.save(self.session))
        return [obj.as_dataclass() for obj in saved_column_objs]

    def filter_entries_by_table(
        self, table: TableCatalogEntry
    ) -> List[ColumnCatalogEntry]:
        try:
            entries = (
                self.session.execute(
                    select(self.model).filter(self.model._table_id == table.row_id)
                )
                .scalars()
                .all()
            )
            return [entry.as_dataclass() for entry in entries]

        except NoResultFound:
            return None
