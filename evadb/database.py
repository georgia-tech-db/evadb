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
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from evadb.catalog.catalog_utils import get_catalog_instance
from evadb.configuration.configuration_manager import ConfigurationManager
from evadb.configuration.constants import DB_DEFAULT_NAME, EvaDB_DATABASE_DIR
from evadb.utils.generic_utils import parse_config_yml

if TYPE_CHECKING:
    from evadb.catalog.catalog_manager import CatalogManager


@dataclass
class EvaDBDatabase:
    db_uri: str
    config: ConfigurationManager
    catalog_uri: str
    catalog_func: Callable

    def catalog(self) -> "CatalogManager":
        """
        Note: Generating an object on demand plays a crucial role in ensuring that different threads do not share the same catalog object, as it can result in serialization issues and incorrect behavior with SQLAlchemy. Refer to get_catalog_instance()
        """
        return self.catalog_func(self.catalog_uri, self.config)


def get_default_db_uri(evadb_dir: Path):
    config_obj = parse_config_yml()
    if config_obj["core"]["catalog_database_uri"]:
        return config_obj["core"]["catalog_database_uri"]
    else:
        # Default to sqlite.
        return f"sqlite:///{evadb_dir.resolve()}/{DB_DEFAULT_NAME}"


def init_evadb_instance(
    db_dir: str, host: str = None, port: int = None, custom_db_uri: str = None
):
    if db_dir is None:
        db_dir = EvaDB_DATABASE_DIR
    config = ConfigurationManager(db_dir)

    catalog_uri = custom_db_uri or get_default_db_uri(Path(db_dir))

    return EvaDBDatabase(db_dir, config, catalog_uri, get_catalog_instance)
