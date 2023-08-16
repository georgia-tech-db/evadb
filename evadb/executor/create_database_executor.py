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
from evadb.models.storage.batch import Batch
from evadb.parser.create_statement import CreateDatabaseStatement
from evadb.utils.logging_manager import logger


class CreateDatabaseExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: CreateDatabaseStatement):
        super().__init__(db, node)

    def exec(self, *args, **kwargs):
        # todo handle if_not_exists

        logger.debug(
            f"Trying to connect to the provided engine {self.node.engine} with params {self.node.param_dict}"
        )
        # todo handle if the provided database params are valid

        logger.debug(f"Creating database {self.node}")

        self.catalog().insert_database_catalog_entry(
            self.node.database_name, self.node.engine, self.node.param_dict
        )

        yield Batch(
            pd.DataFrame(
                [
                    f"The database {self.node.database_name} has been successfully created."
                ]
            )
        )
