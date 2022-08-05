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

from eva.catalog.catalog_manager import CatalogManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.planner.drop_udf_plan import DropUDFPlan
from eva.utils.logging_manager import logger


class DropUDFExecutor(AbstractExecutor):
    def __init__(self, node: DropUDFPlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        """Drop UDF executor

        Calls the catalog to drop udf metadata.
        """
        catalog_manager = CatalogManager()

        # check catalog if it already has this udf entry
        if not catalog_manager.get_udf_by_name(self.node.name):
            err_msg = (
                f"UDF {self.node.name} does not exist, therefore cannot be dropped."
            )
            if self.node.if_exists:
                logger.warn(err_msg)
            else:
                logger.exception(err_msg)
                raise RuntimeError(err_msg)
        else:
            catalog_manager.drop_udf(self.node.name)
            yield Batch(
                pd.DataFrame(
                    {f"UDF {self.node.name} successfully dropped"},
                    index=[0],
                )
            )
