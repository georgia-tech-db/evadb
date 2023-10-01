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
import os

from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from evadb.catalog.catalog_type import VectorStoreType
from evadb.catalog.models.index_catalog import IndexCatalog, IndexCatalogEntry
from evadb.catalog.models.utils import ColumnCatalogEntry
from evadb.catalog.services.base_service import BaseService
from evadb.utils.logging_manager import logger


class IndexCatalogService(BaseService):
    def __init__(self, db_session: Session):
        super().__init__(IndexCatalog, db_session)

    def insert_entry(
        self,
        name: str,
        save_file_path: str,
        type: VectorStoreType,
        feat_column: ColumnCatalogEntry,
        function_signature: str,
        index_def: str,
    ) -> IndexCatalogEntry:
        index_entry = IndexCatalog(
            name,
            save_file_path,
            type,
            feat_column.row_id,
            function_signature,
            index_def,
        )
        index_entry = index_entry.save(self.session)
        return index_entry.as_dataclass()

    def get_entry_by_name(self, name: str) -> IndexCatalogEntry:
        try:
            entry = self.query.filter(self.model._name == name).one()
            return entry.as_dataclass()
        except NoResultFound:
            return None

    def get_entry_by_id(self, id: int) -> IndexCatalogEntry:
        try:
            entry = self.query.filter(self.model._row_id == id).one()
            return entry.as_dataclass()
        except NoResultFound:
            return None

    def get_entry_by_column_and_function_signature(
        self, column: ColumnCatalogEntry, function_signature: str
    ):
        try:
            entry = self.query.filter(
                self.model._feat_column_id == column.row_id,
                self.model._function_signature == function_signature,
            ).one()
            return entry.as_dataclass()
        except NoResultFound:
            return None

    def delete_entry_by_name(self, name: str):
        try:
            index_obj = self.query.filter(self.model._name == name).one()
            index_metadata = index_obj.as_dataclass()
            # clean up the on disk data
            if os.path.exists(index_metadata.save_file_path):
                if os.path.isfile(index_metadata.save_file_path):
                    # For service-hosting-based vector database, we should not
                    # touch their base directory. The only case that needs to
                    # be taken care of is FAISS index local disk file.
                    os.remove(index_metadata.save_file_path)
            index_obj.delete(self.session)
        except Exception:
            logger.exception("Delete index failed for name {}".format(name))
            return False
        return True
