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
from typing import Dict, List

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
DEFAULT_VIDEO_LINK = "https://www.youtube.com/watch?v=-d-w1tL0WBk"

APP_SOURCE_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_VIDEO_PATH = os.path.join(APP_SOURCE_DIR, "benchmarks", "russia_ukraine.mp4")
# temporary file paths
ONLINE_VIDEO_PATH = os.path.join("evadb_data", "tmp", "online_video.mp4")
TRANSCRIPT_PATH = os.path.join("evadb_data", "tmp", "transcript.csv")
SUMMARY_PATH = os.path.join("evadb_data", "tmp", "summary.csv")
BLOG_PATH = "blog.md"


def receive_user_input() -> Dict:
    """Receives user input.

    Returns:
        user_input (dict): global configurations
    """
    print(
        "🔮 Welcome to EvaDB! This app lets you ask questions on any local or"
        " YouTube online video.\nYou will only need to supply a Youtube URL"
        " and an OpenAI API key.\n"
    )
    from_youtube = str(
        input(
            "📹 Are you querying an online Youtube video or a local video?"
            " ('yes' for online/ 'no' for local): "
        )
    ).lower() in ["y", "yes"]
    user_input = {"from_youtube": from_youtube}

    if from_youtube:
        # get Youtube video url
        video_link = str(
            input(
                "🌐 Enter the URL of the YouTube video (press Enter to use our"
                " default Youtube video URL): "
            )
        )

        if video_link == "":
            video_link = DEFAULT_VIDEO_LINK
        user_input["video_link"] = video_link
    else:
        video_local_path = str(
            input(
                "💽 Enter the local path to your video (press Enter to use our"
                " demo video): "
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
        new_line += " " + line["text"]

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
    cursor.query("DROP TABLE IF EXISTS youtube_video;").execute()
    cursor.query(f"LOAD VIDEO '{ONLINE_VIDEO_PATH}' INTO youtube_video;").execute()
    # extract speech texts from videos
    cursor.query("DROP TABLE IF EXISTS youtube_video_text;").execute()
    cursor.query(
        "CREATE TABLE IF NOT EXISTS youtube_video_text AS SELECT"
        " SpeechRecognizer(audio) FROM youtube_video;"
    ).execute()
    print("✅ Video analysis completed.")

    raw_transcript_string = cursor.query("SELECT text FROM youtube_video_text;").df()[
        "youtube_video_text.text"
    ][0]
    return raw_transcript_string


def generate_local_video_transcript(cursor: evadb.EvaDBCursor, video_path: str) -> str:
    """Extracts speech from video for llm processing.

    Args:
        cursor (EVADBCursor): evadb api cursor.
        video_path (str): video path.

    Returns:
        str: video transcript text.
    """
    print(f"\n⏳ Analyzing local video from {video_path}. This may take a" " while...")

    # load youtube video into an evadb table
    cursor.query("DROP TABLE IF EXISTS local_video;").execute()
    cursor.query(f"LOAD VIDEO '{video_path}' INTO local_video;").execute()

    # extract speech texts from videos
    cursor.query("DROP TABLE IF EXISTS local_video_text;").execute()
    cursor.query(
        "CREATE TABLE IF NOT EXISTS local_video_text AS SELECT"
        " SpeechRecognizer(audio) FROM local_video;"
    ).execute()
    print("✅ Video analysis completed.")

    # retrieve generated transcript
    raw_transcript_string = cursor.query("SELECT text FROM local_video_text;").df()[
        "local_video_text.text"
    ][0]
    return raw_transcript_string


def generate_summary(cursor: evadb.EvaDBCursor):
    """Generate summary of a video transcript if it is too long (exceeds llm token limits)

    Args:
        cursor (EVADBCursor): evadb api cursor.
    """
    transcript_list = cursor.query("SELECT text FROM Transcript;").df()[
        "transcript.text"
    ]
    if len(transcript_list) == 1:
        summary = transcript_list[0]
        df = pd.DataFrame([{"summary": summary}])
        df.to_csv(SUMMARY_PATH)

        cursor.query("DROP TABLE IF EXISTS Summary;").execute()
        cursor.query(
            """CREATE TABLE IF NOT EXISTS Summary (summary TEXT(100));"""
        ).execute()
        cursor.query(f"LOAD CSV '{SUMMARY_PATH}' INTO Summary;").execute()
        return

    generate_summary_text_query = (
        "SELECT ChatGPT('summarize the video in detail', text) FROM" " Transcript;"
    )
    responses = cursor.query(generate_summary_text_query).df()["chatgpt.response"]
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

        cursor.query("DROP TABLE IF EXISTS Summary;").execute()
        cursor.query(
            """CREATE TABLE IF NOT EXISTS Summary (summary TEXT(100));"""
        ).execute()
        cursor.query(f"LOAD CSV '{SUMMARY_PATH}' INTO Summary;").execute()

        generate_summary_text_query = (
            "SELECT ChatGPT('summarize in detail', summary) FROM Summary;"
        )
        responses = cursor.query(generate_summary_text_query).df()["chatgpt.response"]
        summary = " ".join(responses)

        # no further summarization is needed if the summary is short enough
        if len(summary) <= MAX_CHUNK_SIZE:
            need_to_summarize = False

    # load final summary to table
    cursor.query("DROP TABLE IF EXISTS Summary;").execute()
    cursor.query(
        """CREATE TABLE IF NOT EXISTS Summary (summary TEXT(100));"""
    ).execute()
    cursor.query(f"LOAD CSV '{SUMMARY_PATH}' INTO Summary;").execute()


def generate_response(cursor: evadb.EvaDBCursor, question: str) -> str:
    """Generates question response with llm.

    Args:
        cursor (EVADBCursor): evadb api cursor.
        question (str): question to ask to llm.

    Returns
        str: response from llm.
    """
    # generate summary
    if len(cursor.query("SELECT text FROM Transcript;").df()["transcript.text"]) == 1:
        return cursor.query(
            f"SELECT ChatGPT('{question}', text) FROM Transcript;"
        ).df()["chatgpt.response"][0]
    else:
        if not os.path.exists(SUMMARY_PATH):
            generate_summary(cursor)

        return cursor.query(
            f"SELECT ChatGPT('{question}', summary) FROM Summary;"
        ).df()["chatgpt.response"][0]


def generate_blog_sections(cursor: evadb.EvaDBCursor) -> List:
    """Generates logical sections of the blog post.

    Args:
        cursor (EVADBCursor): evadb api cursor.

    Returns
        List: list of blog sections
    """
    sections_query = (
        "list 7 logical sections of a blog post from the transcript as a" " python list"
    )
    sections_string = str(
        cursor.query(f"SELECT ChatGPT('{sections_query}', summary) FROM Summary;").df()[
            "chatgpt.response"
        ][0]
    )
    begin = sections_string.find("[")
    end = sections_string.find("]")
    assert begin != -1 and end != -1, "cannot infer blog sections."

    sections_string = sections_string[begin + 1 : end]
    sections_string = sections_string.replace("\n", "")
    sections_string = sections_string.replace("\t", "")
    sections_string = sections_string.replace('"', "")

    sections = sections_string.split(",")
    for i in range(len(sections)):
        sections[i] = sections[i].strip()
    print(sections)
    return sections


def generate_blog_post(cursor: evadb.EvaDBCursor):
    """Generates blog post.

    Args:
        cursor (EVADBCursor): evadb api cursor.
    """

    to_generate = str(
        input(
            "\nWould you like to generate a blog post based on the video?" " (yes/no): "
        )
    )
    if to_generate.lower() == "yes" or to_generate.lower() == "y":
        print("⏳ Generating blog post (may take a while)...")

        if not os.path.exists(SUMMARY_PATH):
            generate_summary(cursor)

        # use llm to generate blog post
        sections = generate_blog_sections(cursor)

        title_query = "generate a creative title of a blog post from the transcript"
        generate_title_rel = cursor.query(
            f"SELECT ChatGPT('{title_query}', summary) FROM Summary;"
        )
        blog = "# " + generate_title_rel.df()["chatgpt.response"][0].replace('"', "")

        i = 1
        for section in sections:
            print(f"--⏳ Generating body ({i}/{len(sections)}) titled" f" {section}...")
            if "introduction" in section.lower():
                section_query = f"write a section about {section} from transcript"
                section_prompt = (
                    "generate response in markdown format and highlight"
                    " important technical terms with hyperlinks"
                )
            elif "conclusion" in section.lower():
                section_query = "write a creative conclusion from transcript"
                section_prompt = "generate response in markdown format"
            else:
                section_query = (
                    "write a single detailed section about"
                    f" {section} from transcript"
                )
                section_prompt = (
                    "generate response in markdown format with information"
                    " from the internet"
                )

            generate_section_rel = cursor.query(
                f"SELECT ChatGPT('{section_query}', summary,"
                f" '{section_prompt}') FROM Summary;"
            )

            generated_section = generate_section_rel.df()["chatgpt.response"][0]
            print(generated_section)
            blog += "\n" + generated_section + "\n"
            i += 1

        source_query = (
            "generate a short list of keywords for the transcript with" " hyperlinks"
        )
        source_prompt = "generate response in markdown format"
        print("--⏳ Wrapping up...")
        generate_source_rel = cursor.query(
            f"SELECT ChatGPT('{source_query}', summary,"
            f" '{source_prompt}') FROM Summary;"
        )
        blog += "\n## Sources\n" + generate_source_rel.df()["chatgpt.response"][0]
        print(blog)

        if os.path.exists(BLOG_PATH):
            os.remove(BLOG_PATH)

        with open(BLOG_PATH, "w") as file:
            file.write(blog)

        print(f"✅ blog post is saved to file {os.path.abspath(BLOG_PATH)}")


def cleanup():
    """Removes any temporary file / directory created by EvaDB."""
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
                "Failed to download video transcript. Downloading video and"
                " generate transcript from video instead..."
            )

    try:
        # establish evadb api cursor
        cursor = evadb.connect().cursor()

        raw_transcript_string = None
        if transcript is not None:
            raw_transcript_string = group_transcript(transcript)
        else:
            # create speech recognizer function from HuggingFace

            speech_analyzer_function_query = """
                CREATE FUNCTION SpeechRecognizer
                TYPE HuggingFace
                TASK 'automatic-speech-recognition'
                MODEL 'openai/whisper-base';
            """
            cursor.query(speech_analyzer_function_query).execute()

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

        if raw_transcript_string is not None:
            partitioned_transcript = partition_transcript(raw_transcript_string)
            df = pd.DataFrame(partitioned_transcript)
            df.to_csv(TRANSCRIPT_PATH)

        # load chunked transcript into table
        cursor.query("DROP TABLE IF EXISTS Transcript;").execute()
        cursor.query(
            """CREATE TABLE IF NOT EXISTS Transcript (text TEXT(50));"""
        ).execute()
        cursor.query(f"LOAD CSV '{TRANSCRIPT_PATH}' INTO Transcript;").execute()

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
                response = generate_response(cursor, question)
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
