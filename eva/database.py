# coding=utf-8
# Copyright 2018-2023 EVA
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
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from eva.catalog.catalog_manager import CatalogManager, get_catalog_instance
from eva.configuration.configuration_manager import ConfigurationManager
from eva.configuration.constants import DB_DEFAULT_NAME, EVA_DATABASE_DIR


@dataclass
class EVADB:
    db_uri: str
    config: ConfigurationManager
    catalog_uri: str
    catalog_func: Callable

    def catalog(self) -> CatalogManager:
        """
        Note: Generating an object on demand plays a crucial role in ensuring that different threads do not share the same catalog object, as it can result in serialization issues and incorrect behavior with SQLAlchemy. Refer to get_catalog_instance()
        """
        return self.catalog_func(self.catalog_uri, self.config)


def get_default_db_uri(eva_db_dir: Path):
    return f"sqlite:///{eva_db_dir.resolve()}/{DB_DEFAULT_NAME}"


def init_eva_db_instance(
    db_dir: str, host: str = None, port: int = None, custom_db_uri: str = None
):
    if db_dir is None:
        db_dir = EVA_DATABASE_DIR
    config = ConfigurationManager(db_dir)

    catalog_uri = custom_db_uri or get_default_db_uri(Path(db_dir))

    return EVADB(db_dir, config, catalog_uri, get_catalog_instance)
