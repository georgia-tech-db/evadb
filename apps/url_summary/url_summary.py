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
import shutil

import pandas as pd
import validators
from langchain.document_loaders import UnstructuredURLLoader

import evadb

DEFAULT_URL = "https://alphasec.io/what-are-passkeys/"


def cleanup():
    """Removes any temporary file / directory created by EvaDB."""
    if os.path.exists("summary.csv"):
        os.remove("summary.csv")
    if os.path.exists("evadb_data"):
        shutil.rmtree("evadb_data")


if __name__ == "__main__":
    print("🔮 Welcome to EvaDB! This app lets you summarize the content of any URL.\n")

    # Get OpenAI key if needed
    try:
        api_key = os.environ["OPENAI_KEY"]
    except KeyError:
        api_key = str(input("🔑 Enter your OpenAI API key: "))
        os.environ["OPENAI_KEY"] = api_key

    try:
        # Get the url
        url_link = str(input("🔗 Enter the URL (press Enter to use our default URL) : "))

        if url_link == "":
            url_link = DEFAULT_URL

        if not validators.url(url_link):
            raise Exception("Please enter a valid URL.")

        print("\n⏳ Loading URL data\n")
        url_data = UnstructuredURLLoader(urls=[url_link]).load()

        df = pd.DataFrame({"text": [url_data]})
        df.to_csv("summary.csv")
        print(df)

        print("📶 Establishing evadb api cursor connection.")
        cursor = evadb.connect().cursor()

        # Load summary into table
        cursor.drop_table("URL_Summary", if_exists=True).execute()
        cursor.query(
            """CREATE TABLE IF NOT EXISTS URL_Summary (text TEXT(4096));"""
        ).execute()
        cursor.load("summary.csv", "URL_Summary", "csv").execute()

        # Generate summary with chatgpt udf
        print("⏳ Generating Summary (may take a while)... \n")
        query = "Create a summary of the provided content in 250-300 words."
        generate_chatgpt_response_rel = cursor.table("URL_Summary").select(
            f"ChatGPT('{query}', text)"
        )
        responses = generate_chatgpt_response_rel.df()["chatgpt.response"]
        print(responses[0], "\n")

        cleanup()
        print("✅ Session ended.")
        print("===========================================")
    except Exception as e:
        cleanup()
        print("❗️ Session ended with error : ", e)
        print(e)
        print("===========================================")
