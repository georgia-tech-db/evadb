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
from typing import Dict

import pandas as pd
from pytube import YouTube, extract
from youtube_transcript_api import YouTubeTranscriptApi

import evadb

MAX_CHUNK_SIZE = 10000
DEFAULT_VIDEO_LINK = "https://www.youtube.com/watch?v=TvS1lHEQoKk"
DEFAULT_VIDEO_PATH = "./apps/youtube_qa/benchmarks/russia_ukraine.mp4"


def receive_user_input() -> Dict:
    """Receives user input.

    Returns:
        user_input (dict): global configurations
    """
    print(
        "🔮 Welcome to EvaDB! This app lets you ask questions on any local or YouTube online video.\nYou will only need to supply a Youtube URL and an OpenAI API key.\n\n"
    )
    from_youtube = str(
        input("📹 Are you using a YouTube video online? (y/n): ")
    ).lower() in ["y", "yes"]
    user_input = {"from_youtube": from_youtube}

    if from_youtube:
        # get Youtube video url
        video_link = str(
            input(
                "📺 Enter the URL of the YouTube video (press Enter to use a default Youtube video): "
            )
        )

        if video_link == "":
            video_link = DEFAULT_VIDEO_LINK
        user_input["video_link"] = video_link
    else:
        video_local_path = str(
            input(
                "📺 Enter the local path to your video (press Enter to use our demo video): "
            )
        )

        if video_local_path == "":
            video_local_path = DEFAULT_VIDEO_PATH
        user_input["video_local_path"] = video_local_path

    # get OpenAI key if needed
    try:
        api_key = os.environ["OPENAI_KEY"]
    except KeyError:
        api_key = str(input("🔑 Enter your OpenAI API key: "))
        os.environ["OPENAI_KEY"] = api_key

    return user_input


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
    video_id = extract.video_id(video_link)
    print("⏳ Transcript download in progress...")
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    print("✅ Video transcript downloaded successfully.")
    return transcript


def download_youtube_video_from_link(video_link: str):
    """Downloads a YouTube video from url.

    Args:
        video_link (str): url of the target YouTube video.
    """
    yt = YouTube(video_link).streams.first()
    try:
        print("⏳ video download in progress...")
        yt.download(filename="online_video.mp4")
    except Exception as e:
        print(f"⛔️ Video download failed with error: \n{e}")
    print("✅ Video downloaded successfully.")


def generate_online_video_transcript(cursor: evadb.EvaDBCursor) -> str:
    """Extracts speech from video for llm processing.

    Args:
        cursor (EVADBCursor): evadb api cursor.

    Returns:
        str: video transcript text.
    """
    print("\n⏳ Analyzing YouTube video. This may take a while...")

    # load youtube video into an evadb table
    cursor.drop_table("youtube_video", if_exists=True).execute()
    cursor.load("online_video.mp4", "youtube_video", "video").execute()

    # extract speech texts from videos
    cursor.drop_table("youtube_video_text", if_exists=True).execute()
    cursor.query(
        "CREATE TABLE IF NOT EXISTS youtube_video_text AS SELECT SpeechRecognizer(audio) FROM youtube_video;"
    ).execute()
    print("✅ Video analysis completed.")

    raw_transcript_string = (
        cursor.table("youtube_video_text")
        .select("text")
        .df()["youtube_video_text.text"][0]
    )
    return raw_transcript_string


def generate_local_video_transcript(cursor: evadb.EvaDBCursor, video_path: str) -> str:
    """Extracts speech from video for llm processing.

    Args:
        cursor (EVADBCursor): evadb api cursor.
        video_path (str): video path.

    Returns:
        str: video transcript text.
    """
    print(f"\n⏳ Analyzing local video from {video_path}. This may take a while...")

    # load youtube video into an evadb table
    cursor.drop_table("local_video", if_exists=True).execute()
    cursor.load(video_path, "local_video", "video").execute()

    # extract speech texts from videos
    cursor.drop_table("local_video_text", if_exists=True).execute()
    cursor.query(
        "CREATE TABLE IF NOT EXISTS local_video_text AS SELECT SpeechRecognizer(audio) FROM local_video;"
    ).execute()
    print("✅ Video analysis completed.")

    # retrieve generated transcript
    raw_transcript_string = (
        cursor.table("local_video_text").select("text").df()["local_video_text.text"][0]
    )
    return raw_transcript_string


def generate_blog_post(cursor: evadb.EvaDBCursor) -> str:
    to_generate = str(
        input("\nWould you like to generate a blog post of the video? (y/n): ")
    )
    if to_generate.lower() == "y":
        print("⏳ Generating blog post (may take a while)...")

        # generate video summary
        generate_chatgpt_summary_rel = cursor.table("Transcript").select(
            "ChatGPT('summarize this video', text)"
        )
        responses = generate_chatgpt_summary_rel.df()["chatgpt.response"]

        summary = ""
        for r in responses:
            summary += f"{r} \n"

        # save summary to csv
        df = pd.DataFrame([{"summary": summary}])
        df.to_csv("./evadb_data/tmp/summary.csv")

        # load summary to db
        cursor.drop_table("Summary", if_exists=True).execute()
        cursor.query(
            """CREATE TABLE IF NOT EXISTS Summary (summary TEXT(100));"""
        ).execute()
        cursor.load("./evadb_data/tmp/summary.csv", "Summary", "csv").execute()

        # use llm to generate blog post
        generate_blog_rel = cursor.table("Summary").select(
            "ChatGPT('generate a blog post of the video summary', summary)"
        )
        responses = generate_blog_rel.df()["chatgpt.response"]
        blog = responses[0]
        print(blog)

        if os.path.exists("blog.txt"):
            os.remove("blog.txt")

        with open("blog.txt", "w") as file:
            file.write(blog)

        print("✅ blog post is saved to file blog.txt")


def cleanup():
    """Removes any temporary file / directory created by EvaDB."""
    if os.path.exists("online_video.mp4"):
        os.remove("online_video.mp4")
    if os.path.exists("evadb_data"):
        shutil.rmtree("evadb_data")


if __name__ == "__main__":
    # receive input from user
    user_input = receive_user_input()

    # load YouTube video transcript if it is available online
    transcript = None
    if user_input["from_youtube"]:
        try:
            transcript = download_youtube_video_transcript(user_input["video_link"])
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
            df.to_csv("./evadb_data/tmp/transcript.csv")
        else:
            # create speech recognizer UDF from HuggingFace
            args = {
                "task": "automatic-speech-recognition",
                "model": "openai/whisper-base",
            }
            speech_analyzer_udf_rel = cursor.create_udf(
                "SpeechRecognizer", type="HuggingFace", **args
            )
            speech_analyzer_udf_rel.execute()

            if user_input["from_youtube"]:
                # download youtube video online if the video disabled transcript
                download_youtube_video_from_link(user_input["video_link"])

            # generate video transcript if the transcript is not availble online or if the video is local
            raw_transcript_string = (
                generate_online_video_transcript(cursor)
                if user_input["from_youtube"]
                else generate_local_video_transcript(
                    cursor, user_input["video_local_path"]
                )
            )

            partitioned_transcript = partition_transcript(raw_transcript_string)
            df = pd.DataFrame(partitioned_transcript)
            df.to_csv("./evadb_data/tmp/transcript.csv")
            df.to_csv("./transcript.csv")

        # load chunked transcript into table
        cursor.drop_table("Transcript", if_exists=True).execute()
        cursor.query(
            """CREATE TABLE IF NOT EXISTS Transcript (text TEXT(50));"""
        ).execute()
        cursor.load("./evadb_data/tmp/transcript.csv", "Transcript", "csv").execute()

        print("===========================================")
        print("🪄 Ask anything about the video!")
        ready = True
        while ready:
            question = str(input("Question (enter 'exit' to exit): "))
            if question.lower() == "exit":
                ready = False
            else:
                # Generate response with chatgpt udf
                print("⏳ Generating response (may take a while)...")
                generate_chatgpt_response_rel = cursor.table("Transcript").select(
                    f"ChatGPT('given this video, {question} (in 100 words)', text)"
                )
                responses = generate_chatgpt_response_rel.df()["chatgpt.response"]

                response = ""
                for r in responses:
                    response += f"{r} \n"
                print(response, "\n")
                print("✅ Answer:")

        # generate a blog post on user demand
        generate_blog_post(cursor)

        cleanup()
        print("✅ Session ended.")
        print("===========================================")
    except Exception as e:
        cleanup()
        print("❗️ Session ended with an error.")
        print(e)
        print("===========================================")
