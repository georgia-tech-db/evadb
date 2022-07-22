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

from eva.catalog.catalog_manager import CatalogManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.planner.drop_udf_plan import DropUDFPlan


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
            err_msg = "UDF: {} does not exsit".format(self.node.name)
            if self.node.if_exists:
                logger.warn(err_msg)
            else:
                logger.exception(err_msg)
        response_code = catalog_manager.drop_udf(self.node.name)