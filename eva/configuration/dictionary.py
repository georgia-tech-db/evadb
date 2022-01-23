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
from pathlib import Path

import eva

EVA_INSTALLATION_DIR = os.path.dirname(eva.__file__)
EVA_DEFAULT_DIR = str(Path.home()) + "/.eva/"
EVA_DATASET_DIR = "eva_datasets"
EVA_CONFIG_FILE = "eva.yml"
CATALOG_DIR = "catalog"
DATASET_DATAFRAME_NAME = "dataset"
DB_DEFAULT_URI = "sqlite:///{}eva_catalog.db".format(EVA_DEFAULT_DIR)
