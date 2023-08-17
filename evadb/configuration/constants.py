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
from pathlib import Path

import evadb

EvaDB_INSTALLATION_DIR = Path(evadb.__file__).parent
EvaDB_ROOT_DIR = Path(evadb.__file__).parent.parent
EvaDB_DATABASE_DIR = "evadb_data"
EvaDB_APPS_DIR = "apps"
EvaDB_DATASET_DIR = "evadb_datasets"
EvaDB_CONFIG_FILE = "evadb.yml"
UDF_DIR = "udfs"
MODEL_DIR = "models"
CATALOG_DIR = "catalog"
INDEX_DIR = "index"
CACHE_DIR = "cache"
DATASET_DATAFRAME_NAME = "dataset"
DB_DEFAULT_NAME = "evadb.db"
S3_DOWNLOAD_DIR = "s3_downloads"
TMP_DIR = "tmp"
DEFAULT_TRAIN_TIME_LIMIT = 120
