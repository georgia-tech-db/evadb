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

MAX_CHUNK_SIZE = 10000
DEFAULT_VIDEO_LINK = "https://www.youtube.com/watch?v=TvS1lHEQoKk"
DEFAULT_VIDEO_PATH = "./apps/youtube_qa/benchmarks/russia_ukraine.mp4"

# temporary file paths
ONLINE_VIDEO_PATH = "./evadb_data/tmp/online_video.mp4"
TRANSCRIPT_PATH = "./evadb_data/tmp/transcript.csv"
SUMMARY_PATH = "./evadb_data/tmp/summary.csv"
BLOG_PATH = "blog.md"


def receive_user_input() -> Dict:
    """Receives user input.

    Returns:
        user_input (dict): global configurations
    """
    print(
        "🔮 Welcome to EvaDB! This app lets you ask questions on any local or YouTube online video.\nYou will only need to supply a Youtube URL and an OpenAI API key.\n\n"
    )
    from_youtube = str(
        input(
            "📹 Are you querying an online Youtube video or a local video? ('yes' for online/ 'no' for local): "
        )
    ).lower() in ["y", "yes"]
    user_input = {"from_youtube": from_youtube}

    if from_youtube:
        # get Youtube video url
        video_link = str(
            input(
                "📺 Enter the URL of the YouTube video (press Enter to use our default Youtube video URL): "
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
        api_key = str(input("🔑 Enter your OpenAI key: "))
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


def partition_summary(prev_summary: str):
    """Summarize a summary if a summary is too large.

    Args:
        prev_summary (str): previous summary that is too large.

    Returns:
        List: a list of partitioned summary
    """
    k = 2
    while True:
        if (len(prev_summary) / k) <= MAX_CHUNK_SIZE:
            break
        else:
            k += 1
    chunk_size = int(len(prev_summary) / k)

    new_summary = [
        {"summary": prev_summary[i : i + chunk_size]}
        for i in range(0, len(prev_summary), chunk_size)
    ]
    if len(new_summary[-1]["summary"]) < 30:
        new_summary.pop()
    return new_summary


def group_transcript(transcript: dict):
    """Group video transcript elements when they are too short.

    Args:
        transcript (dict): downloaded video transcript as a dictionary.

    Returns:
        str: full transcript as a single string.
    """
    new_line = ""
    for line in transcript:
        new_line += line["text"]

    return new_line


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
    yt = (
        YouTube(video_link)
        .streams.filter(file_extension="mp4", progressive="True")
        .first()
    )
    try:
        print("⏳ video download in progress...")
        yt.download(filename=ONLINE_VIDEO_PATH)
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
    cursor.load(ONLINE_VIDEO_PATH, "youtube_video", "video").execute()

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


def generate_summary(cursor: evadb.EvaDBCursor):
    """Generate summary of a video transcript if it is too long (exceeds llm token limits)

    Args:
        cursor (EVADBCursor): evadb api cursor.
    """
    generate_summary_rel = cursor.table("Transcript").select(
        "ChatGPT('summarize the video in detail', text)"
    )
    responses = generate_summary_rel.df()["chatgpt.response"]

    summary = ""
    for r in responses:
        summary += f"{r} \n"
    df = pd.DataFrame([{"summary": summary}])
    df.to_csv(SUMMARY_PATH)

    need_to_summarize = len(summary) > MAX_CHUNK_SIZE
    while need_to_summarize:
        partitioned_summary = partition_summary(summary)

        df = pd.DataFrame([{"summary": partitioned_summary}])
        df.to_csv(SUMMARY_PATH)

        cursor.drop_table("Summary", if_exists=True).execute()
        cursor.query(
            """CREATE TABLE IF NOT EXISTS Summary (summary TEXT(100));"""
        ).execute()
        cursor.load(SUMMARY_PATH, "Summary", "csv").execute()

        generate_summary_rel = cursor.table("Summary").select(
            "ChatGPT('summarize in detail', summary)"
        )
        responses = generate_summary_rel.df()["chatgpt.response"]
        summary = " ".join(responses)

        # no further summarization is needed if the summary is short enough
        if len(summary) <= MAX_CHUNK_SIZE:
            need_to_summarize = False

    # load final summary to table
    cursor.drop_table("Summary", if_exists=True).execute()
    cursor.query(
        """CREATE TABLE IF NOT EXISTS Summary (summary TEXT(100));"""
    ).execute()
    cursor.load(SUMMARY_PATH, "Summary", "csv").execute()


def generate_response(cursor: evadb.EvaDBCursor, df, question: str) -> str:
    """Generates question response with llm.

    Args:
        cursor (EVADBCursor): evadb api cursor.
        question (str): question to ask to llm.

    Returns
        str: response from llm.
    """
    # generate summary
    prompt = f"""There is a dataframe in pandas (python). The name of the
            dataframe is df. This is the result of print(df.head()):
            {df}. Return the python code (do not import anything) to get the answer to the following question: {question}"""
    context = ""

    print(prompt)

    query = cursor.table("Transcript").select(f"ChatGPT('{prompt}', 'country')")

    print(query.sql_query())
    output = query.df()["chatgpt.response"][0]

    return output


def generate_blog_post(cursor: evadb.EvaDBCursor) -> str:
    to_generate = str(
        input("\nWould you like to generate a blog post based on the video? (yes/no): ")
    )
    if to_generate.lower() == "yes" or to_generate.lower() == "y":
        print("⏳ Generating blog post (may take a while)...")

        if not os.path.exists(SUMMARY_PATH):
            generate_summary(cursor)

        # use llm to generate blog post
        generate_blog_rel = cursor.table("Summary").select(
            "ChatGPT('generate a long detailed blog post of the video summary in markdown format that has sections and hyperlinks', summary)"
        )
        responses = generate_blog_rel.df()["chatgpt.response"]
        blog = responses[0]
        print(blog)

        if os.path.exists(BLOG_PATH):
            os.remove(BLOG_PATH)

        with open(BLOG_PATH, "w") as file:
            file.write(blog)

        print(f"✅ blog post is saved to file {BLOG_PATH}")


def cleanup():
    """Removes any temporary file / directory created by EvaDB."""
    # if os.path.exists("evadb_data"):
    #    shutil.rmtree("evadb_data")


if __name__ == "__main__":
    try:
        # establish evadb api cursor
        cursor = evadb.connect().cursor()

        # Sample DataFrame
        df = pd.DataFrame(
            {
                "country": [
                    "United States",
                    "United Kingdom",
                    "France",
                    "Germany",
                    "Italy",
                    "Spain",
                    "Canada",
                    "Australia",
                    "Japan",
                    "China",
                ],
                "gdp": [
                    19294482071552,
                    2891615567872,
                    2411255037952,
                    3435817336832,
                    1745433788416,
                    1181205135360,
                    1607402389504,
                    1490967855104,
                    4380756541440,
                    14631844184064,
                ],
                "happiness_index": [
                    6.94,
                    7.16,
                    6.66,
                    7.07,
                    6.38,
                    6.4,
                    7.23,
                    7.22,
                    5.87,
                    5.12,
                ],
            }
        )

        df.to_csv(TRANSCRIPT_PATH)

        # load chunked transcript into table
        cursor.drop_table("Transcript", if_exists=True).execute()
        cursor.load(TRANSCRIPT_PATH, "Transcript", "Document").execute()

        print("===========================================")
        print("🪄 Ask anything about the dataframe!")
        ready = True
        while ready:
            question = str(input("Question (enter 'exit' to exit): "))
            if question.lower() == "exit":
                ready = False
            else:
                # Generate response with chatgpt udf
                print("⏳ Generating response (may take a while)...")
                response = generate_response(cursor, df, question)
                print("+--------------------------------------------------+")
                print("✅ Answer:")
                print(response)
                print("+--------------------------------------------------+")

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
