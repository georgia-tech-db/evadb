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
import os
import evadb


def load_data():
    path = os.path.dirname(evadb.__file__)
    cursor = evadb.connect(path).cursor()

    embedding_udf = cursor.create_udf(
        udf_name="embedding",
        if_not_exists=True,
        impl_path=f"{path}/udfs/sentence_feature_extractor.py",
    )
    embedding_udf.execute()

    print("Dropping existing tables")
    cursor.drop_table("data_table").execute()
    cursor.drop_table("embedding_table").execute()

    print("Loading PDFs into evadb")
    cursor.load(
        file_regex="source_documents/*.pdf", format="PDF", table_name="data_table"
    ).execute()

    print("Extracting Feature Embeddings. This may take time ...")
    cursor.query(
        "CREATE TABLE IF NOT EXISTS embedding_table AS SELECT embedding(data), data FROM data_table;"
    ).execute()

    print("Building FAISS Index ...")
    cursor.create_vector_index(
        index_name="embedding_index",
        table_name="embedding_table",
        expr="features",
        using="FAISS",
    )


def main():
    load_data()
    print("Ingestion complete! You can now run privateGPT.py to query your documents")


if __name__ == "__main__":
    main()
