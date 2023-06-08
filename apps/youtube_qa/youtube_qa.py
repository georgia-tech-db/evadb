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
import time

from pytube import YouTube

import evadb


def download_youtube_video_from_link(video_link: str):
    """Downloads a YouTube video from url.

    Args:
        video_link (str): url of the target YouTube video.
    """
    start = time.time()
    yt = YouTube(video_link).streams.first()
    try:
        print("Video download in progress...")
        yt.download(filename="online_video.mp4")
    except Exception as e:
        print(f"An error occurred: {e}")
    print(f"Video downloaded successfully in {time.time() - start} seconds")


def analyze_video():
    """Extracts speech from video for llm processing.

    Returns:
        EvaDBDBCursor: evadb api cursor.
    """
    print("Analyzing video. This may take a while...")
    start = time.time()

    # establish evadb api cursor
    cursor = evadb.connect().cursor()

    # bootstrap speech analyzer udf and chatgpt udf for analysis
    args = {"task": "automatic-speech-recognition", "model": "openai/whisper-base"}
    speech_analyzer_udf_rel = cursor.create_udf(
        "SpeechRecognizer", type="HuggingFace", **args
    )
    speech_analyzer_udf_rel.execute()

    # create chatgpt udf from implemententation
    chatgpt_udf_rel = cursor.create_udf(
        "ChatGPT", impl_path="../../evadb/udfs/chatgpt.py"
    )
    chatgpt_udf_rel.execute()

    # load youtube video into an evadb table
    cursor.query("""DROP TABLE IF EXISTS youtube_video;""").execute()
    cursor.load("online_video.mp4", "youtube_video", "video").execute()

    # extract speech texts from videos
    cursor.query(
        "CREATE TABLE IF NOT EXISTS youtube_video_text AS SELECT SpeechRecognizer(audio) FROM youtube_video;"
    ).execute()
    print(f"Video analysis completed in {time.time() - start} seconds.")
    return cursor


def cleanup():
    """Removes any temporary file / directory created by EvaDB."""
    if os.path.exists("online_video.mp4"):
        os.remove("online_video.mp4")
    if os.path.exists("eva_data"):
        shutil.rmtree("eva_data")


if __name__ == "__main__":
    print(
        "Welcome! This app lets you ask questions about any YouTube video. You will only need to supply a Youtube URL and an OpenAI API key."
    )

    # Get Youtube video url
    video_link = str(input("Enter the URL of the YouTube video: "))

    # Get OpenAI key if needed
    try:
        api_key = os.environ["openai_api_key"]
    except KeyError:
        api_key = str(input("Enter your OpenAI API key: "))
        os.environ["openai_api_key"] = api_key

    download_youtube_video_from_link(video_link)

    try:
        cursor = analyze_video()

        print("===========================================")
        print("Ask anything about the video:")
        ready = True
        while ready:
            question = str(input("Question (enter 'exit' to exit): "))
            if question.lower() == "exit":
                ready = False
            else:
                # Generate response with chatgpt udf
                generate_chatgpt_response_rel = cursor.table(
                    "youtube_video_text"
                ).select(f"ChatGPT('{question}', text)")
                start = time.time()
                response = generate_chatgpt_response_rel.df()["chatgpt.response"][0]
                print(f"Answer (generated in {time.time() - start} seconds):")
                print(response, "\n")

        cleanup()
        print("Session ended.")
        print("===========================================")
    except Exception as e:
        print(f"An error occurred: {e}")
        cleanup()
        print("===========================================")
