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
from pathlib import Path

import pandas as pd
import os
import random
import shutil
import zipfile

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.models.table_catalog import TableCatalogEntry
from eva.configuration.configuration_manager import ConfigurationManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError
from eva.models.storage.batch import Batch
from eva.plan_nodes.load_data_plan import LoadDataPlan
from eva.storage.abstract_storage_engine import AbstractStorageEngine
from eva.storage.storage_engine import StorageEngine
from eva.utils.errors import DatasetFileNotFoundError
from eva.utils.logging_manager import logger
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.parser.table_ref import TableInfo
from eva.catalog.sql_config import IDENTIFIER_COLUMN
from eva.catalog.catalog_type import ColumnType, IndexType, TableType
from eva.parser.create_statement import ColumnDefinition


class LoadZIPExecutor(AbstractExecutor):
    def __init__(self, node: LoadDataPlan):
        super().__init__(node)
        self.catalog = CatalogManager()
        self.media_type = self.node.file_options["file_format"]

    def exec(self, *args, **kwargs):
        storage_engine = None
        table_obj = None

        file_path = os.path.join('data', self.node.file_path)

        if not os.path.exists(file_path):
            raise DatasetFileNotFoundError(
                f"Load {self.media_type.name} failed due to no valid files found on path {str(file_path)}"
            )

        extract_path = os.path.join('data', 'dataset', file_path.split("/")[-1].split(".")[0])

        if not os.path.exists(extract_path):
            os.makedirs(extract_path)
            with self.node.file_path.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            dataset_path = os.path.join(extract_path, 'obj_train_data')
            train_ratio = 0.8
            val_ratio = 0.1
            train_folder = "train"
            val_folder = "valid"
            test_folder = "test"
            image_folder = "images"
            label_folder = "labels"

            folders_to_create = [
                os.path.join(extract_path, image_folder, train_folder),
                os.path.join(extract_path, label_folder, train_folder),
                os.path.join(extract_path, image_folder, val_folder),
                os.path.join(extract_path, label_folder, val_folder),
                os.path.join(extract_path, image_folder, test_folder),
                os.path.join(extract_path, label_folder, test_folder),
            ]

            for folder in folders_to_create:
                if not os.path.exists(folder):
                    os.makedirs(folder)
            
            image_files = [f for f in os.listdir(dataset_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
            num_images = len(image_files)
            num_train = int(num_images * train_ratio)
            num_val = int(num_images * val_ratio)
            num_test = num_images - num_train - num_val

            random.shuffle(image_files)
            for i, image_file in enumerate(image_files):
                if i < num_train:
                    target_image_folder = os.path.join(extract_path, image_folder, train_folder)
                    target_label_folder = os.path.join(extract_path, label_folder, train_folder)
                elif i < num_train + num_val:
                    target_image_folder = os.path.join(extract_path, image_folder, val_folder)
                    target_label_folder = os.path.join(extract_path, label_folder, val_folder)
                else:
                    target_image_folder = os.path.join(extract_path, image_folder, test_folder)
                    target_label_folder = os.path.join(extract_path, label_folder, test_folder)

                target_image_file = os.path.join(target_image_folder, image_file)
                target_label_file = os.path.join(target_label_folder, image_file[:-4] + ".txt")

                if not os.path.exists(target_image_file):
                    shutil.copy(os.path.join(dataset_path, image_file), target_image_folder)

                if not os.path.exists(target_label_file):
                    shutil.copy(os.path.join(dataset_path, image_file[:-4] + ".txt"), target_label_folder)

        table_info = self.node.table_info
        database_name = table_info.database_name
        table_name = table_info.table_name
        do_create = False
        table_obj = self.catalog.get_table_catalog_entry(table_name,database_name)

        # files_path = os.path.join(extract_path, "obj_train_data")
        # images = [f for f in os.listdir(files_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        # labels = [f for f in os.listdir(files_path) if f.lower().endswith((".txt"))]
        
        # image_path = []
        # class_id = []
        # x_center = []
        # y_center = []
        # width = []
        # height = []

        # columns = [
        #     ColumnDefinition("image_path", ColumnType.TEXT, None, None),
        #     ColumnDefinition("class_id", ColumnType.INTEGER, None, None),
        #     ColumnDefinition("x_center", ColumnType.FLOAT, None, None),
        #     ColumnDefinition("y_center", ColumnType.FLOAT, None, None),
        #     ColumnDefinition("width", ColumnType.FLOAT, None, None),
        #     ColumnDefinition("height", ColumnType.FLOAT, None, None),
        # ]

        # for image in images:
        #     label_file = os.path.splitext(image)[0] + '.txt'
        #     label_file_path = os.path.join(files_path, label_file)
        #     if label_file in labels:
        #         with open(label_file_path, 'r') as f:
        #             lines = f.readlines()

        #         for line in lines:
        #             class_id_v, x_center_v, y_center_v, width_v, height_v = map(float, line.strip().split())
        #             image_path.append(image)
        #             class_id.append(class_id_v)
        #             x_center.append(x_center_v)
        #             y_center.append(y_center_v)
        #             width.append(width_v)
        #             height.append(height_v)

        
        # if table_obj:
        #     error = f"{table_name} already exist."
        #     logger.error(error)
        #     raise ExecutorError(error)
        
        # else:
        #     table_obj = self.catalog.create_and_insert_table_catalog_entry(
        #         TableInfo(table_name),
        #         columns,
        #         identifier_column=None,
        #         table_type=TableType.STRUCTURED_DATA,
        #     )
        #     do_create = True

        # storage_engine = StorageEngine.factory(table_obj)
        # if do_create:
        #     storage_engine.create(table_obj)

        # storage_engine.write(
        #     table_obj, 
        #     Batch(pd.DataFrame({"image_path": image_path,
        #                         "class_id": class_id,
        #                         "x_center": x_center,
        #                         "y_center": y_center,
        #                         "width": width,
        #                         "height": height})),)

        # yield Batch(
        #         pd.DataFrame(
        #             [
        #                 f"Number of loaded imgae: {str(len(image_path))}"
        #             ]
        #         )
        #     )


        train_path = os.path.join(extract_path, "images", "train")
        val_path = os.path.join(extract_path, "images", "valid")
        nc_path = os.path.join(extract_path, "obj.names")
        with open(nc_path, "r") as f:
            num_classes = len(f.readlines())

        num_train = sum(os.path.isfile(os.path.join(train_path, f)) for f in os.listdir(train_path))
        num_val = sum(os.path.isfile(os.path.join(val_path, f)) for f in os.listdir(val_path))

        data = {
            "train_path": [train_path],
            "num_train": [num_train],
            "val_path": [val_path],
            "num_val": [num_val],
            "num_classes": [num_classes]
        }

        df = pd.DataFrame(data)
    

        columns = [
            ColumnDefinition("train_path", ColumnType.TEXT, None, None),
            ColumnDefinition("num_train", ColumnType.INTEGER, None, None),
            ColumnDefinition("val_path", ColumnType.TEXT, None, None),
            ColumnDefinition("num_val", ColumnType.INTEGER, None, None),
            ColumnDefinition("num_classes", ColumnType.INTEGER, None, None)
        ]

        if table_obj:
            error = f"{table_name} already exist."
            logger.error(error)
            raise ExecutorError(error)
        
        else:
            table_obj = self.catalog.create_and_insert_table_catalog_entry(
                TableInfo(table_name),
                columns,
                identifier_column=None,
                table_type=TableType.STRUCTURED_DATA,
            )
            do_create = True

        storage_engine = StorageEngine.factory(table_obj)
        if do_create:
            storage_engine.create(table_obj)

        storage_engine.write(table_obj, Batch(df),)

        yield Batch(pd.DataFrame({"file_path": [file_path], 
                                  "extract_path": [extract_path],
                                  "train_path": [train_path],
                                  "num_train": [num_train],
                                  "val_path": [val_path],
                                  "num_val": [num_val],
                                  "nc": [num_classes]}))