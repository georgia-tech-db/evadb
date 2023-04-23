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

import pandas as pd

from eva.executor.abstract_executor import AbstractExecutor
from eva.plan_nodes.tune_plan import TunePlan
from eva.models.storage.batch import Batch
from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.services.table_catalog_service import TableCatalogService
from eva.utils.logging_manager import logger
from eva.executor.executor_utils import ExecutorError
from eva.storage.sqlite_storage_engine import SQLStorageEngine
from eva.third_party.yolo_train import train_yolov5


class TuneExecutor(AbstractExecutor):
    def __init__(self, node: TunePlan):
        super().__init__(node)
        self.catalog = CatalogManager()
        self.table = TableCatalogService()
        self.batch = SQLStorageEngine()

    def exec(self, *args, **kwargs):
        table = self.node.table_info
        table_info = table[0]

        table_name = table_info.table_name
        database_name = table_info.database_name
        batch_size = int(self.node.batch_size)
        epochs_size = int(self.node.epochs_size)
        freeze_layer = int(self.node.freeze_layer)
        multi_scale = self.node.multi_scale
        show_train_progress = self.node.show_train_progress

        check_table = self.catalog.check_table_exists(table_name, database_name)

        if check_table == False:
            error = f"{table_name} does not exist."
            logger.error(error)
            raise ExecutorError(error)
        else:
            table_obj = self.table.get_entry_by_name(database_name, table_name)
            table_col = self.batch.read(table_obj)

            for df in table_col:
                for _, row in df.iterrows():
                    train_path = row['train_path']
                    val_path = row['val_path']
                    num_classes = row['num_classes']
        
        training_results = train_yolov5(batch_size, epochs_size, freeze_layer, multi_scale, train_path, val_path, num_classes)

        if show_train_progress:
            yield Batch(pd.DataFrame(training_results))
        else:
            yield Batch(pd.DataFrame(training_results).iloc[-1])
