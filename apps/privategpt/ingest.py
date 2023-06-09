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

path = os.path.dirname(evadb.__file__)


def load_data(path_to_data: str):
    cursor = evadb.connect("apps/evadb_data").cursor()
    embedding_udf = cursor.create_udf(
        udf_name="embedding",
        if_not_exists=True,
        impl_path=f"{path}/udfs/sentence_feature_extractor.py",
    )
    embedding_udf.execute()
    print("Dropping existing data")
    cursor.drop_table("data_table").execute()
    cursor.drop_table("embedding_table").execute()

    print("Loading pdfs into evadb")
    cursor.load(
        file_regex=path_to_data, format="PDF", table_name="data_table"
    ).execute()

    print("Extracting Feature Emebeddings. Time may take time ...")
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
    parser = argparse.ArgumentParser(description="Ingest data into evadb")
    parser.add_argument(
        "--data-directory",
        "-D",
        help="Regex path to the pdf documents",
    )

    args = parser.parse_args()
    if args.data_directory is None:
        print("Please provide the data directory using -D option.")
        exit()
    load_data(args.data_directory)

    print("Ingestion complete! You can now run privateGPT.py to query your documents")


if __name__ == "__main__":
    main()
