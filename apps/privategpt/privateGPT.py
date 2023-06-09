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
from gpt4all import GPT4All

llm = GPT4All("ggml-gpt4all-j-v1.3-groovy")
llm.model.set_thread_count(16)

cursor = evadb.connect().cursor()


def query(question):
    context_docs = (
        cursor.table("data_table")
        .order(f"""Similarity(embedding('{question}'), embedding(data))""")
        .limit(3)
        .select("data")
        .df()
    )

    # Merge all context information.
    context = "; \n".join(context_docs["data_table.data"])

    # run llm
    messages = [
        {"role": "user", "content": f"Here is some context:{context}"},
        {
            "role": "user",
            "content": f"Answer this question based on context: {question}",
        },
    ]
    return llm.chat_completion(messages, verbose=False, streaming=False)


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
