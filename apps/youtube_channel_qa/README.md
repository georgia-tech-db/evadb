# YouTube Channel Question Answering

## Overview
This app enables you to ask questions about any number of YouTube videos effortlessly. Whether you want to inquire about a specific YouTube channel or manually select video IDs, this app has got you covered. It utilizes the power of OpenAI's Language Model to provide insightful responses.

## Setting up the necessary files

yt_video_ids: In case you dont want to ask questions on a particular YouTube Channel, manually list the Video IDs of the YouTube videos you want to ask questions about in this file.

questions: Specify the questions you want to ask. If this file is empty or doesn't exist, the app enters a Question-Answer (QA) loop where you can manually input your questions.

The default video ids correspond to a random selection of videos from the HowTo100M dataset which contains instructional videos spanning a wide range of categories including motorcycles, fashion, gardening, cooking, arts, fitness, etc. The questions specified in the file pertain to these videos.

The default YouTube Channel that the app downloads from is LinusTechTips. This can be altered by changing the
'DEFAULT_CHANNEL_NAME' variable.

## Dependencies

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

