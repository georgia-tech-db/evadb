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

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.configuration.constants import DB_DEFAULT_NAME, EVA_DATABASE_DIR


@dataclass
class EVADB:
    db_uri: str
    config: ConfigurationManager
    catalog: CatalogManager


def get_default_db_uri(eva_db_dir: Path):
    return f"sqlite:///{eva_db_dir.resolve()}/{DB_DEFAULT_NAME}"


def init_eva_db_instance(
    db_dir: str, host: str = None, port: int = None, custom_db_uri: str = None
):
    if db_dir is None:
        db_dir = EVA_DATABASE_DIR
    config = ConfigurationManager(db_dir)

    catalog = None
    if custom_db_uri:
        catalog = CatalogManager(custom_db_uri, config)
    else:
        catalog = CatalogManager(get_default_db_uri(Path(db_dir)), config)

    return EVADB(db_dir, config, catalog)
