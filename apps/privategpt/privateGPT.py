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

cursor = evadb.connect().cursor()

def setup_udfs():

    embedding_udf = cursor.create_udf(udf_name="embedding", if_not_exists=True, impl_path='evadb/udfs/sentence_feature_extractor.py')
    embedding_udf.execute()

    prompt_udf = cursor.create_udf(udf_name="prompt_generator", if_not_exists=True, impl_path='evadb/udfs/prompt_generator.py')
    prompt_udf.execute()

    gpt4all_udf = cursor.create_udf(udf_name="custom_gpt4all", if_not_exists=True, impl_path='evadb/udfs/custom_gpt4all.py')
    gpt4all_udf.execute()



def query(question):
    response = cursor.query(
        f"""SELECT custom_gpt4all(prompt_generator(data, '{question}')) FROM embedding_table
        ORDER BY Similarity(embedding('{question}'),features)
        LIMIT 4;"""
    ).execute()

    return response.frames.iloc[0][0]



setup_udfs()

## Take input of queries from user in a loop
while True:
    question = input("Enter your question: ")
    if question == "exit":
        break
    answer = query(question)

    print("\n\n> Question:")
    print(query)
    print("\n> Answer:")
    print(answer)
