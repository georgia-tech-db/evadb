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
import evadb

from evadb.configuration.constants import EvaDB_ROOT_DIR

def load_data(cursor, path_to_data: str):
    load_pdf = cursor.load(file_regex=path_to_data, format="PDF", table_name="sotu")
    load_pdf.execute()

    emebdding_table = cursor.query("CREATE TABLE IF NOT EXISTS embedding_table AS SELECT embedding(data), data FROM sotu;")
    emebdding_table.execute()

    cursor.create_vector_index(index_name="embedding_index", table_name= "embedding_table", expr="features", using="FAISS")


cursor = evadb.connect().cursor()

load_data(cursor, f"{EvaDB_ROOT_DIR}/data/documents/state_of_the_union.pdf")