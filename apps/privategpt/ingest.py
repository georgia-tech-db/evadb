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
import argparse
import os

import evadb


def load_data(source_folder_path: str):
    path = os.path.dirname(evadb.__file__)
    cursor = evadb.connect(path).cursor()

    # Drop function if it already exists
    cursor.drop_function("embedding").execute()

    # Create function from Python file
    # This function is a sentence feature extractor
    embedding_udf = cursor.create_function(
        udf_name="embedding",
        if_not_exists=True,
        impl_path=f"{path}/udfs/sentence_feature_extractor.py",
    )
    embedding_udf.execute()

    print("🧹 Dropping existing tables in EvaDB")
    cursor.drop_table("data_table").execute()
    cursor.drop_table("embedding_table").execute()

    print("📄 Loading PDFs into EvaDB")
    cursor.load(
        file_regex=f"{source_folder_path}/*.pdf", format="PDF", table_name="data_table"
    ).execute()

    print("🤖 Extracting Feature Embeddings. This may take some time ...")
    cursor.query(
        "CREATE TABLE IF NOT EXISTS embedding_table AS SELECT embedding(data), data FROM data_table;"
    ).execute()

    print("🔍 Building FAISS Index ...")
    cursor.create_vector_index(
        index_name="embedding_index",
        table_name="embedding_table",
        expr="features",
        using="FAISS",
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        help="Path to the directory with documents",
        default="source_documents",
    )

    args = parser.parse_args()

    directory_path = args.directory

    print(f"🔮 Welcome to EvaDB! Ingesting data in `{directory_path}`")

    load_data(source_folder_path=directory_path)

    print(
        "🔥 Data ingestion complete! You can now run `privateGPT.py` to query your loaded data."
    )


if __name__ == "__main__":
    main()
