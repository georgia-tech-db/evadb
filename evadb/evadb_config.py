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

BASE_EVADB_CONFIG = {
    "evadb_installation_dir": "",
    "datasets_dir": "",
    "catalog_database_uri": "",
    "application": "evadb",
    "mode": "release",
    "batch_mem_size": 30000000,
    "gpu_batch_size": 1,  # batch size used for gpu_operations
    "gpu_ids": [0],
    "host": "0.0.0.0",
    "port": 8803,
    "socket_timeout": 60,
    "ray": False,
    "OPENAI_API_KEY": "",
    "PINECONE_API_KEY": "",
    "PINECONE_ENV": "",
    "MILVUS_URI": "",
    "MILVUS_USER": "",
    "MILVUS_PASSWORD": "",
    "MILVUS_DB_NAME": "",
    "MILVUS_TOKEN": "",
}
