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

import pandas as pd

import evadb


def try_to_import_pytube():
    try:
        import pytube  # noqa: F401
    except ImportError:
        raise ValueError(
            """Could not import pytube python package.
                Please install it with `pip install -r requirements.txt`."""
        )


try_to_import_pytube()

from pytube import YouTube, extract  # noqa: E402
from youtube_transcript_api import YouTubeTranscriptApi  # noqa: E402

MAX_CHUNK_SIZE = 5000
DEFAULT_VIDEO_LINK = "https://www.youtube.com/watch?v=TvS1lHEQoKk"


def partition_transcript(raw_transcript: str):
    """Group video transcript elements when they are too large.

    Args:
        transcript (str): downloaded video transcript as a raw string.

    Returns:
        List: a list of partitioned transcript
    """
    if len(raw_transcript) <= MAX_CHUNK_SIZE:
        return [{"text": raw_transcript}]

    k = 2
    while True:
        if (len(raw_transcript) / k) <= MAX_CHUNK_SIZE:
            break
        else:
            k += 1
    chunk_size = int(len(raw_transcript) / k)

    partitioned_transcript = [
        {"text": raw_transcript[i : i + chunk_size]}
        for i in range(0, len(raw_transcript), chunk_size)
    ]
    if len(partitioned_transcript[-1]["text"]) < 30:
        partitioned_transcript.pop()
    return partitioned_transcript


def group_transcript(transcript: dict):
    """Group video transcript elements when they are too short.

    Args:
        transcript (dict): downloaded video transcript as a dictionary.

    Returns:
        List: a list of partitioned transcript
    """
    grouped_transcript = []
    new_line = ""
    for line in transcript:
        if len(new_line) <= MAX_CHUNK_SIZE:
            new_line += line["text"]
        else:
            grouped_transcript.append({"text": new_line})
            new_line = ""

    if grouped_transcript == []:
        return [{"text": new_line}]
    return grouped_transcript


def download_youtube_video_transcript(video_link: str):
    """Downloads a YouTube video's transcript.

    Args:
        video_link (str): url of the target YouTube video.
    """
    start = time.time()
    video_id = extract.video_id(video_link)
    print("Transcript download in progress...")
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    print(f"Video transcript downloaded successfully in {time.time() - start} seconds")
    return transcript


def download_youtube_video_from_link(video_link: str):
    """Downloads a YouTube video from url.

    Args:
        video_link (str): url of the target YouTube video.
    """
    start = time.time()
    yt = (
        YouTube(video_link)
        .streams.filter(file_extension="mp4", progressive="True")
        .first()
    )
    try:
        print("Video download in progress...")
        yt.download(filename="online_video.mp4")
    except Exception as e:
        print(f"Video download failed with error: \n{e}")
    print(f"Video downloaded successfully in {time.time() - start} seconds")


def generate_online_video_transcript(cursor) -> str:
    """Extracts speech from video for llm processing.

    Args:
        cursor (EVADBCursor): evadb api cursor.

    Returns:
        str: video transcript text.
    """
    print("Analyzing video. This may take a while...")
    start = time.time()

    # bootstrap speech analyzer udf and chatgpt udf for analysis
    args = {"task": "automatic-speech-recognition", "model": "openai/whisper-base"}
    speech_analyzer_udf_rel = cursor.create_udf(
        "SpeechRecognizer", type="HuggingFace", **args
    )
    speech_analyzer_udf_rel.execute()

    # load youtube video into an evadb table
    cursor.query("""DROP TABLE IF EXISTS youtube_video;""").execute()
    cursor.load("online_video.mp4", "youtube_video", "video").execute()

    # extract speech texts from videos
    cursor.query(
        "CREATE TABLE IF NOT EXISTS youtube_video_text AS SELECT SpeechRecognizer(audio) FROM youtube_video;"
    ).execute()
    print(f"Video transcript generated in {time.time() - start} seconds.")

    raw_transcript_string = (
        cursor.table("youtube_video_text")
        .select("text")
        .df()["youtube_video_text.text"][0]
    )
    return raw_transcript_string


def cleanup():
    """Removes any temporary file / directory created by EvaDB."""
    if os.path.exists("online_video.mp4"):
        os.remove("online_video.mp4")
    if os.path.exists("transcript.csv"):
        os.remove("transcript.csv")
    if os.path.exists("evadb_data"):
        shutil.rmtree("evadb_data")


if __name__ == "__main__":
    print(
        "🔮 Welcome to EvaDB! This app lets you ask questions on any YouTube video.\nYou will only need to supply a Youtube URL and an OpenAI API key.\n\n"
    )

    # Get Youtube video url
    video_link = str(
        input(
            "📺 Enter the URL of the YouTube video (press Enter to use a default Youtube video):"
        )
    )

    if video_link == "":
        video_link = DEFAULT_VIDEO_LINK

    # Get OpenAI key if needed
    try:
        api_key = os.environ["OPENAI_KEY"]
    except KeyError:
        api_key = str(input("🔥 Enter your OpenAI API key: "))
        os.environ["OPENAI_KEY"] = api_key

    transcript = None
    try:
        transcript = download_youtube_video_transcript(video_link)
    except Exception as e:
        print(e)
        print(
            "Failed to download video transcript. Downloading video and generate transcript from video instead..."
        )

    try:
        # establish evadb api cursor
        cursor = evadb.connect().cursor()

        if transcript is not None:
            grouped_transcript = group_transcript(transcript)
            df = pd.DataFrame(grouped_transcript)
            df.to_csv("transcript.csv")
        else:
            # download youtube video online if the video disabled transcript
            download_youtube_video_from_link(video_link)

            # generate video transcript
            raw_transcript_string = generate_online_video_transcript(cursor)
            partitioned_transcript = partition_transcript(raw_transcript_string)
            df = pd.DataFrame(partitioned_transcript)
            df.to_csv("transcript.csv")

        # load chunked transcript into table
        cursor.query("""DROP TABLE IF EXISTS Transcript;""").execute()
        cursor.query(
            """CREATE TABLE IF NOT EXISTS Transcript (text TEXT(50));"""
        ).execute()
        cursor.load("transcript.csv", "Transcript", "csv").execute()

        print("===========================================")
        print("Ask anything about the video!")
        ready = True
        while ready:
            question = str(input("Question (enter 'exit' to exit): "))
            if question.lower() == "exit":
                ready = False
            else:
                # Generate response with chatgpt udf
                print("Generating response...")
                generate_chatgpt_response_rel = cursor.table("Transcript").select(
                    f"ChatGPT('{question} in 50 words', text)"
                )
                start = time.time()
                responses = generate_chatgpt_response_rel.df()["chatgpt.response"]

                response = ""
                for r in responses:
                    response += f"{r} \n"
                print(f"Answer (generated in {time.time() - start} seconds):")
                print(response, "\n")

        cleanup()
        print("Session ended.")
        print("===========================================")
    except Exception as e:
        cleanup()
        print("Session ended with an error.")
        print(e)
        print("===========================================")
