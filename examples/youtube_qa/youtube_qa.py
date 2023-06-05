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

from eva.interfaces.relational.db import EVADBConnection, connect
from eva.configuration.configuration_manager import ConfigurationManager
from pytube import YouTube

def download_youtube_video_from_link(video_link: str):
    """Downloads a YouTube video from url.

    Args:
        video_link (str): url of the target YouTube video.
    """
    yt = YouTube(video_link).streams.first()
    try:
        print("Video download in progress...")
        yt.download(filename='online_video.mp4')
    except:
        print("An error has occurred")
    print("Video downloaded successfully")


def analyze_video(api_key: str) -> EVADBConnection:
    """Extracts speech from video for llm processing.

    Args:
        api_key (str): openai api key.

    Returns:
        EVADBConnection: evadb api connection.
    """
    print("Analyzing video. This may take a while...")
    
    # establish evadb api connection
    conn = connect()

    # bootstrap speech analyzer udf and chatgpt udf for analysis
    speech_analyzer_udf_query = """
        CREATE UDF IF NOT EXISTS SpeechRecognizer 
        TYPE HuggingFace 
        'task' 'automatic-speech-recognition' 
        'model' 'openai/whisper-base';
        """
    conn.query(speech_analyzer_udf_query).execute()

    chatgpt_udf_query = """CREATE UDF IF NOT EXISTS ChatGPT IMPL 'eva/udfs/chatgpt.py';"""
    conn.query(chatgpt_udf_query).execute()

    # load youtube video into an evadb table
    conn.query("""DROP TABLE IF EXISTS youtube_video;""").execute()
    conn.load("online_video.mp4", "youtube_video", "video").execute()

    # extract speech texts from videos
    conn.query("CREATE TABLE IF NOT EXISTS youtube_video_text AS SELECT SpeechRecognizer(audio) FROM youtube_video;").execute()

    print("Video analysis completed!")
    return conn

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
    video_link = str(input("Enter the URL of the YouTube video: "))

    # Get OpenAI key if needed
    try:
        api_key = os.environ["openai_api_key"]
    except KeyError:
        api_key = str(input("Enter your OpenAI API key: "))
        os.environ["openai_api_key"] = api_key

    download_youtube_video_from_link(video_link)

    try:
        conn = analyze_video(api_key)

        print("===========================================")
        print("Ask anything about the video:")
        ready = True
        while ready:
            question = str(input("Question (enter \'exit\' to exit): "))
            if question.lower() == 'exit':
                ready = False
            else:
                rel = conn.table("youtube_video_text").select(f"ChatGPT('{question}', text)")
                response = rel.df()['chatgpt.response'][0]
                print("Answer:")
                print(response, "\n")
        
        cleanup()
        print("Session ended.")
        print("===========================================")
    except:
        cleanup()
        print("Session ended with an error.")
        print("===========================================")
