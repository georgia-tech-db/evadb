import os
import shutil

from eva.interfaces.relational.db import EVAConnection, connect
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
    print("Video download succeeded")


def analyze_vieo(api_key: str) -> EVAConnection:
    """Extracts speech from video for llm processing.

    Args:
        api_key (str): openai api key.

    Returns:
        EVAConnection: evadb api connection.
    """
    print("Analyzing video. This may take a while...")
    ConfigurationManager().update_value("third_party", "openai_api_key", api_key) # configure api key
    
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

    chatgpt_udf_query = """CREATE UDF IF NOT EXISTS ChatGPT IMPL '../../eva/udfs/chatgpt.py';"""
    conn.query(chatgpt_udf_query).execute()

    # load youtube video into an evadb table
    conn.query("""DROP TABLE IF EXISTS youtube_video;""").execute()
    conn.load("online_video.mp4", "youtube_video", "video").execute()

    # extract speech texts from videos
    conn.query("CREATE TABLE IF NOT EXISTS youtube_video_text AS SELECT SpeechRecognizer(audio) FROM youtube_video;").execute()

    print("Video Analysis Completes!")
    return conn


def cleanup():
    """Removes any temporary file / directory created by EVA.
    """
    if os.path.exists('online_video.mp4'):
        os.remove('online_video.mp4')
    if os.path.exists('eva_data'):
        shutil.rmtree('eva_data')


if __name__ == "__main__":
    print("Welcome! This is a bot powered by EVADB and chatgpt that tells you everything about a youtube video. All you need to do is to enter your video link and openai api key below.")
    video_link = str(input("Enter the url of your YouTube video: "))
    api_key = str(input("Enter your openai api key: "))

    download_youtube_video_from_link(video_link)

    try:
        conn = analyze_vieo(api_key)

        print("===========================================")
        print("Ask us anything about the video (i.e. summarize the video)")
        ready = True
        while ready:
            question = str(input("Ask about the video (enter \'exit\' to exit): "))
            if question.lower() == 'exit':
                ready = False
            else:
                rel = conn.table("youtube_video_text").select(f"ChatGPT('{question}', text)")
                response = rel.df()['chatgpt.response'][0]
                print("Answer:")
                print(response, "\n")
        
        cleanup()
        print("session ended.")
        print("===========================================")
    except:
        cleanup()
        print("session ended with some error.")
        print("===========================================")
