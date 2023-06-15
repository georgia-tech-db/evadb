# YouTube Question Answering

## Overview
This app lets you ask questions across any number of YouTube videos. You will only need to supply the YouTube Video IDs (in 'yt_video_ids' file) and an OpenAI API key.

The questions to ask can be specified in the 'questions' file.

This app is powered by EvaDB's Python API and ChatGPT UDF.

## Setup
Ensure that the local Python version is >= 3.8. Install the required libraries:

```bat
pip install -r requirements.txt
```

## Usage
Run script: 
```bat
python multi_youtube_video_qa.py
```

