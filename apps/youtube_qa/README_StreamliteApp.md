# YouTube Question Answering

## Overview
This app lets you ask questions about any YouTube video. You will only need to supply a Youtube URL and an OpenAI API key.

This app is powered by EvaDB's Python API and ChatGPT UDF.

## Setup
Ensure that the local Python version is >= 3.8. Install the required libraries:

```bat
pip install -r requirements.txt
```

## Enter Your OpenAPI Key
```bat
Please set your OpenAI API key in evadb.yml file (third_party, open_api_key) or environment variable (OPENAI_KEY)
```

## Usage
Run script: 
```bat
streamlit run youtube_streamlit_app.py
```

## Example

<img width="895" alt="YoutubeApp" src="https://github.com/vivek-mandal/eva/assets/46380919/254f2fd5-7ac6-4a57-a968-f1b7cc7106d8">

