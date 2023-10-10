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

"""
EvaDB configuration dict
batch_mem_size configures the number of rows processed by the execution engine in one iteration
rows = max(1, row_mem_size / batch_mem_size)
"""

"""
Configuration split :-

BASE_EVADB_CONFIG
    Configuration parameters for the internal use of the catalog 
    and other services required on startup. These comprise of 
    mostly immutable configurations that do not change in the 
    lifecycle of any EvaDB project. Splitting this helps us combat
    the cyclic dependency issue.

BOOTSTRAP_EVADB_CONFIG
    Configuration parameters that get populated during configuration
    bootstrap. Consists of default values of fairly common mutable
    configurations that can be played around with during experiments.
    These get populated to the catalog table when the 
    ConfigurationManager is initialized.
"""

BASE_EVADB_CONFIG = {
    "evadb_installation_dir": "",
    "catalog_database_uri": "",
    "application": "evadb",
    "mode": "release",
    "host": "0.0.0.0",
    "port": 8803,
    "socket_timeout": 60,

}

BOOTSTRAP_EVADB_CONFIG = {
    "datasets_dir": "",
    "batch_mem_size": 30000000,
    "gpu_batch_size": 1, # batch size used for gpu_operations
    "gpu_ids": [
        0
    ],
    "ray": False,
    "OPENAI_KEY": "",
    "PINECONE_API_KEY": "",
    "PINECONE_ENV": ""
}