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
import os
from typing import List

from sqlalchemy.orm.exc import NoResultFound

from eva.catalog.models.column_catalog import ColumnCatalogEntry
from eva.catalog.models.index_catalog import IndexCatalog, IndexCatalogEntry
from eva.catalog.services.base_service import BaseService
from eva.utils.logging_manager import logger


class IndexCatalogService(BaseService):
    def __init__(self):
        super().__init__(IndexCatalog)

    def insert_entry(
        self,
        name: str,
        save_file_path: str,
        type: str,
        feat_column: ColumnCatalogEntry,
        udf_signature: str,
    ) -> IndexCatalogEntry:
        index_entry = IndexCatalog(
            name, save_file_path, type, feat_column.row_id, udf_signature
        )
        index_entry = index_entry.save()
        return index_entry.as_dataclass()

    def get_entry_by_name(self, name: str) -> IndexCatalogEntry:
        try:
            entry = self.model.query.filter(self.model._name == name).one()
            return entry.as_dataclass()
        except NoResultFound:
            return None

    def get_entry_by_id(self, id: int) -> IndexCatalogEntry:
        try:
            entry = self.model.query.filter(self.model._row_id == id).one()
            return entry.as_dataclass()
        except NoResultFound:
            return None

    def get_entry_by_column_and_udf_signature(
        self, column: ColumnCatalogEntry, udf_signature: str
    ):
        try:
            entry = self.model.query.filter(
                self.model._feat_column_id == column.row_id,
                self.model._udf_signature == udf_signature,
            ).one()
            return entry.as_dataclass()
        except NoResultFound:
            return None

    def delete_entry_by_name(self, name: str):
        try:
            index_obj = self.model.query.filter(self.model._name == name).one()
            index_metadata = index_obj.as_dataclass()
            # clean up the on disk data
            if os.path.exists(index_metadata.save_file_path):
                os.remove(index_metadata.save_file_path)
            index_obj.delete()
        except Exception:
            logger.exception("Delete index failed for name {}".format(name))
            return False
        return True

    def get_all_entries(self) -> List[IndexCatalogEntry]:
        try:
            entries = self.model.query.all()
            return [entry.as_dataclass() for entry in entries]
        except NoResultFound:
            return []
