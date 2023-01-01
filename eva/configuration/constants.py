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
from eva.version import VERSION

EVA_INSTALLATION_DIR = Path(eva.__file__).parent
EVA_ROOT_DIR = Path(eva.__file__).parent.parent
# Using eva version to govern the EVA_DEFAULT_DIR
# This means we won't support backward compatibility as each version will maintain its own copy of database.
# Ideally, if the new release is not breaking backward compatibilty, we can keep using the same copy.
# We can revisit it later
EVA_DEFAULT_DIR = Path.home() / ".eva" / str(VERSION)
EVA_DATASET_DIR = "eva_datasets"
EVA_UPLOAD_DIR = "tmp"
EVA_CONFIG_FILE = "eva.yml"
UDF_DIR = "udfs"
CATALOG_DIR = "catalog"
INDEX_DIR = "index"
DATASET_DATAFRAME_NAME = "dataset"
DB_DEFAULT_URI = "sqlite:///{}/eva_catalog.db".format(EVA_DEFAULT_DIR.resolve())
