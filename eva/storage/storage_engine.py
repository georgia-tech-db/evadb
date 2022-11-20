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
from eva.catalog.catalog_type import TableType
from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.configuration.configuration_manager import ConfigurationManager
from eva.storage.abstract_storage_engine import AbstractStorageEngine
from eva.utils.generic_utils import str_to_class


class StorageEngine:
    storages = {
        TableType.STRUCTURAL_DATA: str_to_class(
            ConfigurationManager().get_value("storage", "engine")
        )(),
        TableType.VIDEO_DATA: str_to_class(
            ConfigurationManager().get_value("storage", "video_engine")
        )(),
    }

    @classmethod
    def factory(cls, table_metadata: DataFrameMetadata) -> AbstractStorageEngine:
        if table_metadata.table_type in cls.storages:
            return cls.storages[table_metadata.table_type]

        raise RuntimeError(f"Invalid table type {table_metadata.table_type}")
