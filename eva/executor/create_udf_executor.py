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
from eva.planner.create_udf_plan import CreateUDFPlan
from eva.utils.generic_utils import path_to_class
from eva.utils.logging_manager import logger


class CreateUDFExecutor(AbstractExecutor):
    def __init__(self, node: CreateUDFPlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        """Create udf executor

        Calls the catalog to create udf metadata.
        """
        catalog_manager = CatalogManager()
        # check catalog if it already has this udf entry
        if catalog_manager.get_udf_by_name(self.node.name):
            if self.node.if_not_exists:
                msg = f"UDF {self.node.name} already exists, nothing added."
                logger.warn(msg)
                yield Batch(pd.DataFrame([msg]))
                return
            else:
                msg = f"UDF {self.node.name} already exists."
                logger.error(msg)
                raise RuntimeError(msg)
        io_list = []
        io_list.extend(self.node.inputs)
        io_list.extend(self.node.outputs)
        impl_path = self.node.impl_path.absolute().as_posix()
        # check if we can create the udf object
        try:
            path_to_class(impl_path, self.node.name)()
        except Exception as e:
            err_msg = (
                f"{str(e)}. Please verify that the UDF class name in the "
                f"implementation file matches the provided UDF name {self.node.name}."
            )
            logger.error(err_msg)
            raise RuntimeError(err_msg)
        catalog_manager.create_udf(
            self.node.name, impl_path, self.node.udf_type, io_list
        )
        yield Batch(
            pd.DataFrame([f"UDF {self.node.name} successfully added to the database."])
        )
