# coding=utf-8
# Copyright 2018-2023 EVA
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


from eva.interfaces.relational.db import connect
from pytube import YouTube

def download_youtube_video_from_link(video_link: str):
    """Downloads a YouTube video from url.

    Args:
        video_link (str): url of the target YouTube video.
    """
    yt = YouTube(video_link).streams.first()
    try:
        print("Video download in progress...")
        start_time = time.time()
        yt.download(filename='online_video.mp4')
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Video downloaded successfully in: {execution_time} seconds")
    except:
        print("An error has occurred during downloading")


def analyze_video(cursor, api_key: str):
    """Extracts speech from video for passing it to ChatGPT

    Args:
        api_key (str): openai api key.

    Returns:
        EVAConnection: evadb api connection.
    """
    print("Analyzing video. This may take a while...")
    start_time = time.time()
    
    # bootstrap speech analyzer udf and chatgpt udf for analysis
    speech_analyzer_udf_query = """
        CREATE UDF IF NOT EXISTS SpeechRecognizer 
        TYPE HuggingFace 
        'task' 'automatic-speech-recognition' 
        'model' 'openai/whisper-base';
        """
    cursor.query(speech_analyzer_udf_query).execute()

    chatgpt_udf_query = """CREATE UDF IF NOT EXISTS ChatGPT IMPL 'eva/udfs/chatgpt.py';"""
    cursor.query(chatgpt_udf_query).execute()

    # load youtube video into an evadb table
    cursor.query("""DROP TABLE IF EXISTS youtube_video;""").execute()
    cursor.load("online_video.mp4", "youtube_video", "video").execute()

    # extract speech texts from videos
    cursor.query("CREATE TABLE IF NOT EXISTS youtube_video_text AS SELECT SpeechRecognizer(audio) FROM youtube_video;").execute()

    print(cursor.query("SELECT * FROM youtube_video_text").df())

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Video analysis completed in: {execution_time} seconds")

def cleanup():
    """Removes any temporary file / directory created by EVA.
    """
    if os.path.exists('online_video.mp4'):
        os.remove('online_video.mp4')
    if os.path.exists('eva_data'):
        shutil.rmtree('eva_data')

if __name__ == "__main__":
    print("Welcome! This app lets you ask questions about any YouTube video. You will only need to supply a Youtube URL and an OpenAI API key.")

    # Get Youtube video url
    video_link = str(input("Enter the URL of your YouTube video (enter nothing to pick the default video):"))

    if video_link == "":
        video_link = "https://www.youtube.com/watch?v=FM7Z-Xq8Drc"

    # Get OpenAI key if needed
    try:
        api_key = os.environ["OPENAI_KEY"]
    except KeyError:
        api_key = str(input("Enter your OpenAI key: "))
        os.environ["OPENAI_KEY"] = api_key

    download_youtube_video_from_link(video_link)

    # establish connection with local EvaDB server
    cursor = connect().cursor()

    try:
        analyze_video(cursor, api_key)

        print("===========================================")
        print("Ask anything about the video:")
        ready = True
        while ready:
            question = str(input("Question (enter \'exit\' to exit): "))
            if question.lower() == 'exit':
                ready = False
            else:
                query = cursor.table("youtube_video_text").select(f"ChatGPT('{question}', text)")
                response = query.df()['chatgpt.response'][0]
                print("Answer:")
                print(response, "\n")
        
        cleanup()
        print("Session ended.")
        print("===========================================")
    except:
        cleanup()
        print("Session ended with an error.")
        print("===========================================")
