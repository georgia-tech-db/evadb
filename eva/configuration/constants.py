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

import eva

EVA_INSTALLATION_DIR = Path(eva.__file__).parent
EVA_ROOT_DIR = Path(eva.__file__).parent.parent
EVA_DATABASE_DIR = "eva_data"
EVA_DATASET_DIR = "eva_datasets"
EVA_CONFIG_FILE = "eva.yml"
UDF_DIR = "udfs"
CATALOG_DIR = "catalog"
INDEX_DIR = "index"
CACHE_DIR = "cache"
DATASET_DATAFRAME_NAME = "dataset"
DB_DEFAULT_NAME = "eva.db"
S3_DOWNLOAD_DIR = "s3_downloads"
TMP_DIR = "tmp"
