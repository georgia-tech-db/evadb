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

from evadb.catalog.catalog_utils import bootstrap_configs, get_catalog_instance
from evadb.configuration.bootstrap_environment import bootstrap_environment
from evadb.configuration.constants import (
    DB_DEFAULT_NAME,
    EvaDB_DATABASE_DIR,
    EvaDB_INSTALLATION_DIR,
)

if TYPE_CHECKING:
    from evadb.catalog.catalog_manager import CatalogManager


@dataclass
class EvaDBDatabase:
    db_uri: str
    catalog_uri: str
    catalog_func: Callable

    def catalog(self) -> "CatalogManager":
        """
        Note: Generating an object on demand plays a crucial role in ensuring that different threads do not share the same catalog object, as it can result in serialization issues and incorrect behavior with SQLAlchemy. Refer to get_catalog_instance()
        """
        return self.catalog_func(self.catalog_uri)


def get_default_db_uri(evadb_dir: Path):
    # Default to sqlite.
    return f"sqlite:///{evadb_dir.resolve()}/{DB_DEFAULT_NAME}"


def init_evadb_instance(
    db_dir: str, host: str = None, port: int = None, custom_db_uri: str = None
):
    if db_dir is None:
        db_dir = EvaDB_DATABASE_DIR

    config_obj = bootstrap_environment(
        Path(db_dir),
        evadb_installation_dir=Path(EvaDB_INSTALLATION_DIR),
    )

    catalog_uri = custom_db_uri or get_default_db_uri(Path(db_dir))

    # load all the config into the configuration_catalog table
    bootstrap_configs(get_catalog_instance(catalog_uri), config_obj)

    return EvaDBDatabase(db_dir, catalog_uri, get_catalog_instance)
