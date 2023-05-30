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
from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager


class EVADB:
    def __init__(self, db_uri: str, config: ConfigurationManager) -> None:
        self._db_uri = db_uri
        self._config = config

        # intialize catalog manager
        self._catalog = CatalogManager(db_uri, config)

    @property
    def catalog(self):
        return self._catalog

    @property
    def config(self):
        return self._config
