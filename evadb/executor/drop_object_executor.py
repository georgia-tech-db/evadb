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


import pandas as pd

from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.executor.executor_utils import ExecutorError, handle_vector_store_params
from evadb.models.storage.batch import Batch
from evadb.parser.types import ObjectType
from evadb.plan_nodes.drop_object_plan import DropObjectPlan
from evadb.storage.storage_engine import StorageEngine
from evadb.third_party.vector_stores.utils import VectorStoreFactory
from evadb.utils.logging_manager import logger


class DropObjectExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: DropObjectPlan):
        super().__init__(db, node)

    def exec(self, *args, **kwargs):
        """Drop Object executor"""

        if self.node.object_type == ObjectType.TABLE:
            yield self._handle_drop_table(self.node.name, self.node.if_exists)

        elif self.node.object_type == ObjectType.INDEX:
            yield self._handle_drop_index(self.node.name, self.node.if_exists)

        elif self.node.object_type == ObjectType.UDF:
            yield self._handle_drop_udf(self.node.name, self.node.if_exists)

    def _handle_drop_table(self, table_name: str, if_exists: bool):
        if not self.catalog().check_table_exists(table_name):
            err_msg = "Table: {} does not exist".format(table_name)
            if if_exists:
                return Batch(pd.DataFrame([err_msg]))
            else:
                raise ExecutorError(err_msg)

        table_obj = self.catalog().get_table_catalog_entry(table_name)
        storage_engine = StorageEngine.factory(self.db, table_obj)

        logger.debug(f"Dropping table {table_name}")
        storage_engine.drop(table=table_obj)

        for col_obj in table_obj.columns:
            for cache in col_obj.dep_caches:
                self.catalog().drop_udf_cache_catalog_entry(cache)

        # todo also delete the indexes associated with the table
        assert self.catalog().delete_table_catalog_entry(
            table_obj
        ), "Failed to drop {}".format(table_name)

        return Batch(
            pd.DataFrame(
                {"Table Successfully dropped: {}".format(table_name)},
                index=[0],
            )
        )

    def _handle_drop_udf(self, udf_name: str, if_exists: bool):
        # check catalog if it already has this udf entry
        if not self.catalog().get_udf_catalog_entry_by_name(udf_name):
            err_msg = f"UDF {udf_name} does not exist, therefore cannot be dropped."
            if if_exists:
                logger.warning(err_msg)
                return Batch(pd.DataFrame([err_msg]))
            else:
                raise RuntimeError(err_msg)
        else:
            udf_entry = self.catalog().get_udf_catalog_entry_by_name(udf_name)
            for cache in udf_entry.dep_caches:
                self.catalog().drop_udf_cache_catalog_entry(cache)

            # todo also delete the indexes associated with the table

            self.catalog().delete_udf_catalog_entry_by_name(udf_name)

            return Batch(
                pd.DataFrame(
                    {f"UDF {udf_name} successfully dropped"},
                    index=[0],
                )
            )

    def _handle_drop_index(self, index_name: str, if_exists: bool):
        index_obj = self.catalog().get_index_catalog_entry_by_name(index_name)
        if not index_obj:
            err_msg = f"Index {index_name} does not exist, therefore cannot be dropped."
            if if_exists:
                logger.warning(err_msg)
                return Batch(pd.DataFrame([err_msg]))
            else:
                raise RuntimeError(err_msg)
        else:
            index = VectorStoreFactory.init_vector_store(
                index_obj.type,
                index_obj.name,
                **handle_vector_store_params(index_obj.type, index_obj.save_file_path),
            )
            assert (
                index is not None
            ), f"Failed to initialize the vector store handler for {index_obj.type}"

            if index:
                index.delete()

            self.catalog().drop_index_catalog_entry(index_name)

            return Batch(
                pd.DataFrame(
                    {f"Index {index_name} successfully dropped"},
                    index=[0],
                )
            )
