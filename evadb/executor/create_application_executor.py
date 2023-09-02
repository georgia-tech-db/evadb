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
from evadb.executor.executor_utils import ExecutorError
from evadb.models.storage.batch import Batch
from evadb.parser.create_statement import CreateApplicationStatement
from evadb.third_party.applications.interface import get_application_handler
from evadb.utils.logging_manager import logger



class CreateApplicationExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: CreateApplicationStatement):
        super().__init__(db, node)

    def exec(self, *args, **kwargs):
        logger.debug(
            f"Trying to connect to the provided engine {self.node.engine} with params {self.node.param_dict}"
        )

        # Check if application already exists.
        app_catalog_entry = self.catalog().get_application_catalog_entry(
            self.node.application_name
        )
        if app_catalog_entry is not None:
            raise ExecutorError(f"{self.node.application_name} already exists.")

        # Check the validity of application entry.
        handler = get_application_handler(self.node.engine, **self.node.param_dict)
        resp = handler.connect()
        if not resp.status:
            raise ExecutorError(f"Cannot establish connection due to {resp.error}")

        logger.debug(f"Creating application {self.node}")
        self.catalog().insert_application_catalog_entry(
            self.node.application_name, self.node.engine, self.node.param_dict
        )

        yield Batch(
            pd.DataFrame(
                [
                    f"The application {self.node.application_name} has been successfully created."
                ]
            )
        )
