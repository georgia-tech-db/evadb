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

from gpt4all import GPT4All

import evadb

path = os.path.dirname(evadb.__file__)
cursor = evadb.connect(path).cursor()


def query(question):
    context_docs = cursor.query(
        f"""
        SELECT data
        FROM embedding_table
        ORDER BY Similarity(embedding('{question}'), features)
        LIMIT 5;
    """
    ).df()

    # Merge all context information.
    context = "\n".join(context_docs["embedding_table.data"])

    # run llm
    llm = GPT4All("ggml-model-gpt4all-falcon-q4_0.bin")
    llm.set_thread_count(16)

    message = f"""If the context is not relevant, please answer the question by using your own knowledge about the topic.
    
    {context}
    
    Question : {question}"""

    answer = llm.generate(message)

    print("\n> Answer:", answer)


print(
    "🔮 Welcome to EvaDB! Don't forget to run `python ingest.py` before"
    " running this file."
)

## Take input of queries from user in a loop
while True:
    question = input("Enter your question (type 'exit' to stop): ")
    if question == "exit" or question == "stop":
        break

    query(question)
