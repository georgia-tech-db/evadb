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
from pytube import YouTube, extract
from youtube_transcript_api import YouTubeTranscriptApi

import evadb

MAX_CHUNK_SIZE = 5000
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


def group_transcript(transcript: dict, grouped_transcript : list):
    """Group video transcript elements when they are too short.

    Args:
        transcript (dict): downloadeded video transcript as a dictionary.

    Returns:
        List: a list of grouped transcripts
    """
    new_line = ""
    title_text = transcript[0]['text']
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
    print(title)
    video_id = extract.video_id(video_link)
    transcript = [{}]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    transcript.insert(0, {'text': "Title : '" + title + "', Summary : "})

    time_taken = time.time() - start
    total_transcription_time += time_taken
    print(f"Video transcript downloaded successfully in {time_taken} seconds \n")
    return transcript


def download_youtube_video_from_link(video_link: str):
    """Downloads a YouTube video from url.

    Args:
        video_link (str): url of the target YouTube video.
    """
    start = time.time()
    yt = YouTube(video_link).streams.filter(file_extension='mp4', progressive='True').first()
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
    speech_analyzer_udf_rel = cursor.create_udf(
        "SpeechRecognizer", type="HuggingFace", **args
    )
    speech_analyzer_udf_rel.execute()

    # load youtube video into an evadb table
    cursor.query("""DROP TABLE IF EXISTS youtube_video;""").execute()
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


def cleanup():
    """Removes any temporary file / directory created by EvaDB."""
    current_directory = os.getcwd()
    files = os.listdir(current_directory)
    mp4_files = [file for file in files if file.endswith(".mp4")]
    if os.path.exists("transcript.csv"):
        os.remove("transcript.csv")
    if os.path.exists("evadb_data"):
        shutil.rmtree("evadb_data")


if __name__ == "__main__":
    print(
        "🔮 Welcome to EvaDB! This app lets you ask questions across any number of YouTube videos.\nYou will only need to supply the video URLs and an OpenAI API key.\n\n"
    )

    # Get OpenAI key if needed
    try:
        api_key = os.environ["OPENAI_KEY"]
    except KeyError:
        api_key = str(input("🔥 Enter your OpenAI API key: "))
        os.environ["OPENAI_KEY"] = api_key

    transcripts = []
    failed_download_links = []
    print("Downloading YT videos")
    link=open('yt_video_ids', 'r')
    for id in link:
        yt_url = "https://www.youtube.com/watch?v=" + id;
        print("Downloading : ", yt_url)
        try:
            transcripts.append(download_youtube_video_transcript(yt_url))
        except Exception as e:
            print(e)
            print(
                "Failed to download video transcript. Will try downloading video and generating transcript later..."
            )
            failed_download_links.append(yt_url)
            continue
    

    try:
        print("establish evadb api cursor")
        cursor = evadb.connect().cursor()

        grouped_transcript = []
        print("Create transcript csv")
        if len(transcripts) > 0:
            for transcript in transcripts:
                group_transcript(transcript, grouped_transcript)

            # print(grouped_transcript)
            df = pd.DataFrame(grouped_transcript)
            # df = pd.DataFrame(transcripts) 
            # print(df)
            if os.path.exists("transcript.csv"):
                df.to_csv("transcript.csv", mode='a')
            else:
                df.to_csv("transcript.csv")

        print("Failed downloads : ", failed_download_links)

        # download youtube video online if the video disabled transcript
        for yt_url in failed_download_links:
            print("Downloading : ", yt_url)
            try:
                download_youtube_video_from_link(yt_url)
            except Exception as e:
                print(f"Downloading {yt_url} failed with ", e)
                continue
        
        # generate video transcript for the downloaded videos
        current_directory = os.getcwd()
        files = os.listdir(current_directory)
        mp4_files = [file for file in files if file.endswith(".mp4")]
        if not mp4_files:
            print("No mp4 files found in current directory. Not generating video transcripts .....")
        else:
            raw_transcript_string = generate_online_video_transcript(cursor)           
            partitioned_transcript = partition_transcript(raw_transcript_string)
            df = pd.DataFrame(partitioned_transcript)
            print(df)
            if os.path.exists("transcript.csv"):
                df.to_csv("transcript.csv", mode='a')
            else:
                df.to_csv("transcript.csv")

        print("Total transcription time : ", total_transcription_time)

        load_start_time = time.time()
        # load chunked transcript into table
        cursor.query("""DROP TABLE IF EXISTS Transcript;""").execute()
        cursor.query(
            """CREATE TABLE IF NOT EXISTS Transcript (text TEXT(100));"""
        ).execute()
        cursor.load("transcript.csv", "Transcript", "csv").execute()
        print(f"Loading transcripts into DB took {time.time() - load_start_time} seconds")
        
        print("Creating embeddings and Vector Index")
        
        udf_query = """CREATE UDF IF NOT EXISTS embedding
            IMPL  '../../../evadb/udfs/sentence_feature_extractor.py';
            """
        cursor.query("DROP UDF IF EXISTS embedding;").execute()
        cursor.query(udf_query).execute()

        cursor.query("DROP UDF IF EXISTS ChatGPT;").execute()
        cursor.query(""" CREATE UDF IF NOT EXISTS ChatGPT
          IMPL '../../../evadb/udfs/chatgpt.py';""").execute()

        cursor.drop_table("embedding_table").execute()
        est = time.time()
        cursor.query(
            f"""CREATE TABLE embedding_table AS
            SELECT embedding(text), text FROM Transcript;"""
        ).execute()
        eft = time.time()
        print(f"Creating embeddings took {eft - est} seconds")

        # Create search index on extracted features.
        cursor.query(
            f"CREATE INDEX faiss_index ON embedding_table (features) USING FAISS;"
        ).execute()

        vet = time.time()
        print(f"Creating index took {vet - eft} seconds")

        questions = open('questions', 'r')
        st = time.time()
        for question in questions:
            print(question)
            question_start = time.time()
            
            # instead of passing all the documents to the LLM, we first do a
            # semantic search over the embeddings and get the most relevant rows.
            cursor.query("DROP TABLE IF EXISTS EMBED_TEXT;").execute()
            text_summarization_query = f"""
                CREATE MATERIALIZED VIEW 
                EMBED_TEXT(text) AS 
                SELECT text FROM embedding_table
                ORDER BY Similarity(embedding('{question}'), features) DESC
                LIMIT 3; 
                """
            cursor.query(text_summarization_query).execute()
            print(cursor.table('EMBED_TEXT').select("*").execute())

            chatgpt_udf = """
                SELECT ChatGPT(f"{question}", text) 
                FROM EMBED_TEXT;
            """
            start = time.time()
            print(f"Time taken to create materialized view {start - question_start}")
            generate_chatgpt_response_rel = cursor.table("EMBED_TEXT").select(
                f"ChatGPT('{question}', text)"
            )
            responses = generate_chatgpt_response_rel.df()["chatgpt.response"]
            print(f"Answer (generated in {time.time() - start} seconds):")
            print(responses[0], "\n")

        print("Total time taken in answering all questions = ", str(time.time() - st))
        cleanup()
        print("Session ended.")
        print("===========================================")
    except Exception as e:
        cleanup()
        print("Session ended with an error.")
        print(e)
        print("===========================================")
