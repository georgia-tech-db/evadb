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
from eva.configuration.constants import EVA_DEFAULT_DIR
from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.plan_nodes.create_udf_plan import CreateUDFPlan
from eva.third_party.huggingface.create import gen_hf_io_catalog_entries
from eva.udfs.decorators.utils import load_io_from_udf_decorators
from eva.utils.errors import UDFIODefinitionError
from eva.utils.generic_utils import load_udf_class_from_file
from eva.utils.logging_manager import logger


class CreateUDFExecutor(AbstractExecutor):
    def __init__(self, node: CreateUDFPlan):
        super().__init__(node)

    def handle_huggingface_udf(self):
        """Handle HuggingFace UDFs

        HuggingFace UDFs are special UDFs that are not loaded from a file.
        So we do not need to call the setup method on them like we do for other UDFs.
        """
        impl_path = f"{EVA_DEFAULT_DIR}/udfs/abstract/hf_abstract_udf.py"
        io_list = gen_hf_io_catalog_entries(self.node.name, self.node.metadata)
        return (
            self.node.name,
            impl_path,
            self.node.udf_type,
            io_list,
            self.node.metadata,
        )

    def handle_generic_udf(self):
        """Handle generic UDFs

        Generic UDFs are loaded from a file. We check for inputs passed by the user during CREATE or try to load io from decorators.
        """
        # load the udf class from the file
        impl_path = self.node.impl_path.absolute().as_posix()
        try:
            # loading the udf class from the file
            udf = load_udf_class_from_file(impl_path, self.node.name)
            # initializing the udf class calls the setup method internally
            udf()
        except Exception as e:
            err_msg = f"Error creating UDF: {str(e)}"
            logger.error(err_msg)
            raise RuntimeError(err_msg)

        io_list = []
        try:
            if self.node.inputs:
                io_list.extend(self.node.inputs)
            else:
                # try to load the inputs from decorators, the inputs from CREATE statement take precedence
                io_list.extend(load_io_from_udf_decorators(udf, is_input=True))

            if self.node.outputs:
                io_list.extend(self.node.outputs)
            else:
                # try to load the outputs from decorators, the outputs from CREATE statement take precedence
                io_list.extend(load_io_from_udf_decorators(udf, is_input=False))
        except UDFIODefinitionError as e:
            err_msg = f"Error creating UDF, input/output definition incorrect: {str(e)}"
            logger.error(err_msg)
            raise RuntimeError(err_msg)
        return (
            self.node.name,
            impl_path,
            self.node.udf_type,
            io_list,
            self.node.metadata,
        )

    def exec(self, *args, **kwargs):
        """Create udf executor

        Calls the catalog to insert a udf catalog entry.
        """
        catalog_manager = CatalogManager()
        # check catalog if it already has this udf entry
        if catalog_manager.get_udf_catalog_entry_by_name(self.node.name):
            if self.node.if_not_exists:
                msg = f"UDF {self.node.name} already exists, nothing added."
                logger.warn(msg)
                yield Batch(pd.DataFrame([msg]))
                return
            else:
                msg = f"UDF {self.node.name} already exists."
                logger.error(msg)
                raise RuntimeError(msg)

        # if it's a type of HuggingFaceModel, override the impl_path
        if self.node.udf_type == "HuggingFace":
            name, impl_path, udf_type, io_list, metadata = self.handle_huggingface_udf()
        else:
            name, impl_path, udf_type, io_list, metadata = self.handle_generic_udf()

        catalog_manager.insert_udf_catalog_entry(
            name, impl_path, udf_type, io_list, metadata
        )
        yield Batch(
            pd.DataFrame([f"UDF {self.node.name} successfully added to the database."])
        )
