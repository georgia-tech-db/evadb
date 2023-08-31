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
from pathlib import Path
from typing import Dict, List

import pandas as pd

from evadb.catalog.catalog_utils import get_metadata_properties
from evadb.catalog.models.udf_catalog import UdfCatalogEntry
from evadb.catalog.models.udf_io_catalog import UdfIOCatalogEntry
from evadb.catalog.models.udf_metadata_catalog import UdfMetadataCatalogEntry
from evadb.configuration.constants import (
    DEFAULT_TRAIN_TIME_LIMIT,
    EvaDB_INSTALLATION_DIR,
)
from evadb.database import EvaDBDatabase
from evadb.executor.abstract_executor import AbstractExecutor
from evadb.models.storage.batch import Batch
from evadb.plan_nodes.create_udf_plan import CreateUDFPlan
from evadb.third_party.huggingface.create import gen_hf_io_catalog_entries
from evadb.udfs.decorators.utils import load_io_from_udf_decorators
from evadb.utils.errors import UDFIODefinitionError
from evadb.utils.generic_utils import (
    load_udf_class_from_file,
    try_to_import_ludwig,
    try_to_import_torch,
    try_to_import_ultralytics,
    try_to_import_forecast
)
from evadb.utils.logging_manager import logger
import hashlib
import pickle
from pathlib import Path
import pudb

class CreateUDFExecutor(AbstractExecutor):
    def __init__(self, db: EvaDBDatabase, node: CreateUDFPlan):
        super().__init__(db, node)
        self.udf_dir = Path(EvaDB_INSTALLATION_DIR) / "udfs"

    def handle_huggingface_udf(self):
        """Handle HuggingFace UDFs

        HuggingFace UDFs are special UDFs that are not loaded from a file.
        So we do not need to call the setup method on them like we do for other UDFs.
        """
        # We need atleast one deep learning framework for HuggingFace
        # Torch or Tensorflow
        try_to_import_torch()
        impl_path = f"{self.udf_dir}/abstract/hf_abstract_udf.py"
        io_list = gen_hf_io_catalog_entries(self.node.name, self.node.metadata)
        return (
            self.node.name,
            impl_path,
            self.node.udf_type,
            io_list,
            self.node.metadata,
        )

    def handle_ludwig_udf(self):
        """Handle ludwig UDFs

        Use ludwig's auto_train engine to train/tune models.
        """
        try_to_import_ludwig()
        from ludwig.automl import auto_train

        assert (
            len(self.children) == 1
        ), "Create ludwig UDF expects 1 child, finds {}.".format(len(self.children))

        aggregated_batch_list = []
        child = self.children[0]
        for batch in child.exec():
            aggregated_batch_list.append(batch)
        aggregated_batch = Batch.concat(aggregated_batch_list, copy=False)
        aggregated_batch.drop_column_alias()

        arg_map = {arg.key: arg.value for arg in self.node.metadata}
        auto_train_results = auto_train(
            dataset=aggregated_batch.frames,
            target=arg_map["predict"],
            tune_for_memory=arg_map.get("tune_for_memory", False),
            time_limit_s=arg_map.get("time_limit", DEFAULT_TRAIN_TIME_LIMIT),
            output_directory=self.db.config.get_value("storage", "tmp_dir"),
        )
        model_path = os.path.join(
            self.db.config.get_value("storage", "model_dir"), self.node.name
        )
        auto_train_results.best_model.save(model_path)
        self.node.metadata.append(UdfMetadataCatalogEntry("model_path", model_path))

        impl_path = Path(f"{self.udf_dir}/ludwig.py").absolute().as_posix()
        io_list = self._resolve_udf_io(None)
        return (
            self.node.name,
            impl_path,
            self.node.udf_type,
            io_list,
            self.node.metadata,
        )

    def handle_ultralytics_udf(self):
        """Handle Ultralytics UDFs"""
        try_to_import_ultralytics()

        impl_path = (
            Path(f"{self.udf_dir}/yolo_object_detector.py").absolute().as_posix()
        )
        udf = self._try_initializing_udf(
            impl_path, udf_args=get_metadata_properties(self.node)
        )
        io_list = self._resolve_udf_io(udf)
        return (
            self.node.name,
            impl_path,
            self.node.udf_type,
            io_list,
            self.node.metadata,
        )

    def handle_forecasting_udf(self):
        """Handle forecasting UDFs"""
        aggregated_batch_list = []
        child = self.children[0]
        for batch in child.exec():
            aggregated_batch_list.append(batch)
        aggregated_batch = Batch.concat(aggregated_batch_list, copy=False)
        aggregated_batch.drop_column_alias()

        arg_map = {arg.key: arg.value for arg in self.node.metadata}
        if not self.node.impl_path:
            impl_path = Path(f"{self.udf_dir}/forecast.py").absolute().as_posix()
        else:
            impl_path = self.node.impl_path.absolute().as_posix()
        arg_map = {arg.key: arg.value for arg in self.node.metadata}

        if "model" not in arg_map.keys(): arg_map["model"] = "AutoARIMA"
        if "frequency" not in arg_map.keys(): arg_map["frequency"] = "M"

        model_name = arg_map["model"]
        frequency = arg_map["frequency"]

        try_to_import_forecast()
        from statsforecast import StatsForecast
        from statsforecast.models import AutoARIMA, AutoCES, AutoETS, AutoTheta


        model_dict = {
            "AutoARIMA": AutoARIMA,
            "AutoCES": AutoCES,
            "AutoETS": AutoETS,
            "AutoTheta": AutoTheta,
        }

        season_dict = {  # https://pandas.pydata.org/docs/user_guide/timeseries.html#timeseries-offset-aliases
            "H": 24,
            "M": 12,
            "Q": 4,
            "SM": 24,
            "BM": 12,
            "BMS": 12,
            "BQ": 4,
            "BH": 24,
            }
        # pu.db
        new_freq = frequency.split("-")[0] if "-" in frequency else frequency  # shortens longer frequencies like Q-DEC
        season_length = season_dict[new_freq] if new_freq in season_dict else 1
        model = StatsForecast([model_dict[model_name](season_length=season_length)], freq=new_freq)

        model_dir = os.path.join(
            self.db.config.get_value("storage", "model_dir"), self.node.name
        )
        Path(model_dir).mkdir(parents=True, exist_ok=True)
        model_path = os.path.join(
            self.db.config.get_value("storage", "model_dir"), self.node.name, str(hashlib.sha256(aggregated_batch.frames.to_string().encode()).hexdigest())+".pkl"
        )

        weight_file = Path(model_path)


        if not weight_file.exists():
            model.fit(aggregated_batch.frames)
            weights = model.fitted_[0][0].model_
            f = open(model_path, "wb")
            pickle.dump(weights, f)
            f.close()

        arg_map_here = {"model": model, "model_path": model_path}
        udf = self._try_initializing_udf(impl_path, arg_map_here)
        io_list = self._resolve_udf_io(udf)

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
        impl_path = self.node.impl_path.absolute().as_posix()
        udf = self._try_initializing_udf(impl_path)
        io_list = self._resolve_udf_io(udf)

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
        # check catalog if it already has this udf entry
        if self.catalog().get_udf_catalog_entry_by_name(self.node.name):
            if self.node.if_not_exists:
                msg = f"UDF {self.node.name} already exists, nothing added."
                yield Batch(pd.DataFrame([msg]))
                return
            else:
                msg = f"UDF {self.node.name} already exists."
                logger.error(msg)
                raise RuntimeError(msg)

        # if it's a type of HuggingFaceModel, override the impl_path
        if self.node.udf_type == "HuggingFace":
            name, impl_path, udf_type, io_list, metadata = self.handle_huggingface_udf()
        elif self.node.udf_type == "ultralytics":
            name, impl_path, udf_type, io_list, metadata = self.handle_ultralytics_udf()
        elif self.node.udf_type == "Ludwig":
            name, impl_path, udf_type, io_list, metadata = self.handle_ludwig_udf()
        elif self.node.udf_type == "Forecasting":
            name, impl_path, udf_type, io_list, metadata = self.handle_forecasting_udf()
        else:
            name, impl_path, udf_type, io_list, metadata = self.handle_generic_udf()

        self.catalog().insert_udf_catalog_entry(
            name, impl_path, udf_type, io_list, metadata
        )
        yield Batch(
            pd.DataFrame([f"UDF {self.node.name} successfully added to the database."])
        )

    def _try_initializing_udf(
        self, impl_path: str, udf_args: Dict = {}
    ) -> UdfCatalogEntry:
        """Attempts to initialize UDF given the implementation file path and arguments.

        Args:
            impl_path (str): The file path of the UDF implementation file.
            udf_args (Dict, optional): Dictionary of arguments to pass to the UDF. Defaults to {}.

        Returns:
            UdfCatalogEntry: A UdfCatalogEntry object that represents the initialized UDF.

        Raises:
            RuntimeError: If an error occurs while initializing the UDF.
        """

        # load the udf class from the file
        try:
            # loading the udf class from the file
            udf = load_udf_class_from_file(impl_path, self.node.name)
            # initializing the udf class calls the setup method internally
            udf(**udf_args)
        except Exception as e:
            err_msg = f"Error creating UDF: {str(e)}"
            # logger.error(err_msg)
            raise RuntimeError(err_msg)

        return udf

    def _resolve_udf_io(self, udf: UdfCatalogEntry) -> List[UdfIOCatalogEntry]:
        """Private method that resolves the input/output definitions for a given UDF.
        It first searches for the input/outputs in the CREATE statement. If not found, it resolves them using decorators. If not found there as well, it raises an error.

        Args:
            udf (UdfCatalogEntry): The UDF for which to resolve input and output definitions.

        Returns:
            A List of UdfIOCatalogEntry objects that represent the resolved input and
            output definitions for the UDF.

        Raises:
            RuntimeError: If an error occurs while resolving the UDF input/output
            definitions.
        """
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

        return io_list
