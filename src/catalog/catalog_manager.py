# coding=utf-8
# Copyright 2018-2020 EVA
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

from pyspark.sql import Row

from src.spark.session import Session
from src.utils.configuration_manager import ConfigurationManager
from src.utils.logging_manager import LoggingManager
from src.utils.logging_manager import LoggingLevel

CATALOG_DIR = "catalog"


class CatalogManager(object):

    _instance = None
    _catalog = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CatalogManager, cls).__new__(cls)

            cls._instance.bootstrap_catalog()

        return cls._instance

    def bootstrap_catalog(self):

        eva_dir = ConfigurationManager().get_value("core", "location")
        output_url = os.path.join(eva_dir, CATALOG_DIR)
        LoggingManager().log("Bootstrapping catalog" + str(output_url),
                             LoggingLevel.INFO)

        spark = Session().get_session()
        sc = Session().get_context()

        squaresDF = spark.createDataFrame(sc.parallelize(range(1, 6))
                                          .map(lambda i:
                                               Row(single=i, double=i ** 2)))

        squaresDF.show(2)
