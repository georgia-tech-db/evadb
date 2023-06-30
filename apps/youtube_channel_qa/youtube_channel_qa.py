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
import scrapetube
from pytube import YouTube, extract
from youtube_transcript_api import YouTubeTranscriptApi

import evadb

MAX_CHUNK_SIZE = 10000
CHATGPT_UDF_PATH = "../../evadb/udfs/chatgpt.py"
SENTENCE_FEATURE_EXTRACTOR_UDF_PATH = "../../evadb/udfs/sentence_feature_extractor.py"
QUESTIONS_PATH = "./questions.txt"
YT_VIDEO_IDS_PATH = "./yt_video_ids.txt"

DEFAULT_CHANNEL_NAME = "LinusTechTips"
DEFAULT_SORTING_ORDER = "popular"

total_transcription_time = 0


def partition_transcript(raw_transcript: str):
    """Parition video transcript elements when they are too large.

    Args:
        transcript (str): downloadeded video transcript as a raw string.

    Returns:
        List: a list of partitioned transcripts
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


def group_transcript(transcript: dict, grouped_transcript: list):
    """Group video transcript elements when they are too short.

    Args:
        transcript (dict): downloadeded video transcript as a dictionary.

    Returns:
        List: a list of grouped transcripts
    """
    new_line = ""
    title_text = transcript[0]["text"]
    for line in transcript:
        if len(new_line) <= MAX_CHUNK_SIZE:
            new_line += " " + line["text"]
        else:
            grouped_transcript.append({"text": new_line})
            new_line = title_text

    if new_line:
        grouped_transcript.append({"text": new_line})
    return grouped_transcript


def download_youtube_video_transcript(video_link: str):
    """Downloads a YouTube video's transcript.

    Args:
        video_link (str): url of the target YouTube video.
    """
    global total_transcription_time
    start = time.time()
    title = YouTube(video_link).streams[0].title
    print(f"Video Title : {title}")
    video_id = extract.video_id(video_link)
    print(f"Video id : {video_id} ")
    transcript = [{}]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    transcript.insert(0, {"text": "Title : '" + title + "', Summary : "})

    time_taken = time.time() - start
    total_transcription_time += time_taken
    print(f"✅ Video transcript downloaded successfully in {time_taken} seconds \n")
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
        yt.download()
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
    global total_transcription_time

    print("Analyzing videos. This may take a while...")
    start = time.time()

    # bootstrap speech analyzer udf and chatgpt udf for analysis
    args = {"task": "automatic-speech-recognition", "model": "openai/whisper-base"}
    speech_analyzer_udf_rel = cursor.create_function(
        "SpeechRecognizer", type="HuggingFace", **args
    )
    speech_analyzer_udf_rel.execute()

    # load youtube video into an evadb table
    cursor.drop_table("youtube_video", if_exists=True).execute()
    cursor.load("*.mp4", "youtube_video", "video").execute()

    # extract speech texts from videos
    cursor.query(
        "CREATE TABLE IF NOT EXISTS youtube_video_text AS SELECT SpeechRecognizer(audio) FROM youtube_video;"
    ).execute()
    print(f"Video transcript generated in {time.time() - start} seconds.")
    total_transcription_time += time.time() - start

    raw_transcript_string = (
        cursor.table("youtube_video_text")
        .select("text")
        .df()["youtube_video_text.text"][0]
    )
    return raw_transcript_string


def generate_response(cursor: evadb.EvaDBCursor, question: str) -> str:
    """Generates question response with llm.

    Args:
        cursor (EVADBCursor): evadb api cursor.
        question (str): question to ask to llm.

    Returns
        str: response from llm.
    """

    # instead of passing all the documents to the LLM, we first do a
    # semantic search over the embeddings and get the most relevant rows.
    cursor.drop_table("EMBED_TEXT", if_exists=True).execute()
    text_summarization_query = f"""
        CREATE TABLE EMBED_TEXT AS
        SELECT text FROM embedding_table
        ORDER BY Similarity(embedding('{question}'), features) DESC
        LIMIT 3;
        """

    cursor.query(text_summarization_query).execute()

    start = time.time()
    prompt = "Answer the questions based on context alone. Do no generate responses on your own."
    generate_chatgpt_response_rel = cursor.table("EMBED_TEXT").select(
        f"ChatGPT('{question}', text, '{prompt}')"
    )
    responses = generate_chatgpt_response_rel.df()["chatgpt.response"]
    print(f"Answer (generated in {time.time() - start} seconds):")
    print(responses[0], "\n")


def cleanup():
    """Removes any temporary file / directory created by EvaDB."""
    if os.path.exists("transcript.csv"):
        os.remove("transcript.csv")
    if os.path.exists("evadb_data"):
        shutil.rmtree("evadb_data")


if __name__ == "__main__":
    print(
        "🔮 Welcome to EvaDB! This app lets you ask questions on any YouTube channel.\n\n"
    )

    yt_video_ids = []
    # get Youtube video url
    channel_name = str(
        input(
            "📺 Enter the Channel Name (press Enter to use our default Youtube Channel) : "
        )
    )

    if channel_name == "":
        channel_name = DEFAULT_CHANNEL_NAME

    limit = input(
        "Enter the number of videos to download (press Enter to download one video) : "
    )

    if limit == "":
        limit = 1
    else:
        limit = int(limit)

    sort_by = str(
        input(
            "Enter the order in which to retrieve the videos (Either 'newest' / 'oldest' / 'popular'). Press Enter to go with 'popular' option : "
        )
    ).lower()

    if sort_by not in ["newest", "oldest", "popular"]:
        sort_by = DEFAULT_SORTING_ORDER

    print(
        "\nWill download",
        limit if limit else "all",
        f"videos from {channel_name} in {sort_by} order\n",
    )

    video_ids = scrapetube.get_channel(
        channel_username=channel_name, limit=limit, sort_by=sort_by
    )

    for video in video_ids:
        yt_video_ids.append(video["videoId"])

    # Get OpenAI key if needed
    try:
        api_key = os.environ["OPENAI_KEY"]
    except KeyError:
        api_key = str(input("🔑 Enter your OpenAI API key: "))
        os.environ["OPENAI_KEY"] = api_key

    transcripts = []
    failed_download_links = []
    print("\nDownloading YT videos\n")

    for id in yt_video_ids:
        yt_url = "https://www.youtube.com/watch?v=" + id
        print("⏳ Downloading : ", yt_url)
        try:
            transcripts.append(download_youtube_video_transcript(yt_url))
        except Exception as e:
            print(e)
            print(
                "❗️ Failed to download video transcript. Will try downloading video and generating transcript later... \n\n"
            )
            failed_download_links.append(yt_url)
            continue

    try:
        grouped_transcript = []
        if len(transcripts) > 0:
            for transcript in transcripts:
                group_transcript(transcript, grouped_transcript)

            df = pd.DataFrame(grouped_transcript)
            if os.path.exists("transcript.csv"):
                df.to_csv("transcript.csv", mode="a")
            else:
                df.to_csv("transcript.csv")

        print(f"Failed downloads : {failed_download_links}\n")

        # download youtube video online if the video disabled transcript
        for yt_url in failed_download_links:
            print(f"Downloading : {yt_url}")
            try:
                download_youtube_video_from_link(yt_url)
            except Exception as e:
                print(f"Downloading {yt_url} failed with {e} \n")
                continue

        print("⏳ Establishing evadb api cursor connection.")
        cursor = evadb.connect().cursor()

        # generate video transcript for the downloaded videos
        current_directory = os.getcwd()
        files = os.listdir(current_directory)
        mp4_files = [file for file in files if file.endswith(".mp4")]
        if not mp4_files:
            print(
                "No mp4 files found in current directory. Not generating video transcripts ..."
            )
        else:
            raw_transcript_string = generate_online_video_transcript(cursor)
            partitioned_transcript = partition_transcript(raw_transcript_string)
            df = pd.DataFrame(partitioned_transcript)
            print(df)
            if os.path.exists("transcript.csv"):
                df.to_csv("transcript.csv", mode="a")
            else:
                df.to_csv("transcript.csv")

        print("Total transcription time : ", total_transcription_time)

        load_start_time = time.time()
        # load chunked transcript into table
        cursor.drop_table("Transcript", if_exists=True).execute()
        cursor.query(
            """CREATE TABLE IF NOT EXISTS Transcript (text TEXT(100));"""
        ).execute()
        cursor.load("transcript.csv", "Transcript", "csv").execute()
        print(
            f"Loading transcripts into DB took {time.time() - load_start_time} seconds"
        )

        print("Creating embeddings and Vector Index")

        cursor.drop_function("embedding", if_exists=True).execute()
        cursor.create_function(
            "embedding",
            if_not_exists=True,
            impl_path=SENTENCE_FEATURE_EXTRACTOR_UDF_PATH,
        ).execute()

        cursor.drop_table("embedding_table", if_exists=True).execute()
        est = time.time()
        cursor.query(
            """CREATE TABLE embedding_table AS
            SELECT embedding(text), text FROM Transcript;
            """
        ).execute()
        eft = time.time()
        print(f"Creating embeddings took {eft - est} seconds")

        # Create search index on extracted features.
        cursor.create_vector_index(
            index_name="faiss_index",
            table_name="embedding_table",
            expr="features",
            using="FAISS",
        ).df()

        vet = time.time()
        print(f"Creating index took {vet - eft} seconds")

        questions = []
        if os.path.isfile(QUESTIONS_PATH) and os.path.getsize(QUESTIONS_PATH) > 0:
            questions = open(QUESTIONS_PATH, "r")
            st = time.time()
            for question in questions:
                print(question)
                generate_response(cursor, question)
            print(
                "Total time taken in answering all questions = ", str(time.time() - st)
            )
        else:  # Enter a QA Loop.
            ready = True
            while ready:
                question = str(input("Question (enter 'exit' to exit): "))
                if question.lower() == "exit":
                    ready = False
                else:
                    # Generate response with chatgpt udf
                    print("⏳ Generating response (may take a while)...")
                    generate_response(cursor, question)
        cleanup()
        print("✅ Session ended.")
        print("===========================================")
    except Exception as e:
        cleanup()
        print("❗️ Session ended with an error.")
        print(e)
        print("===========================================")
