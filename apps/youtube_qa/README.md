# YouTube Question Answering

## Overview
This app lets you ask questions about any YouTube video. You will only need to supply a Youtube URL and an OpenAI API key.

This app is powered by EvaDB's Python API and ChatGPT UDF.

## Setup
Ensure that the local Python version is >= 3.8. Install the required libraries:

```bat
pip install -r requirements.txt
```

## Usage
Run script: 
```bat
python youtube_qa.py
```

## Example

```bat
📺 Enter the URL of the YouTube video (press Enter to use a default YouTube video): https://www.youtube.com/watch?v=TvS1lHEQoKk
🔥 Enter your OpenAI API key: sk-*****

===========================================
Ask anything about the video!

Question (enter 'exit' to exit): summarize this video
Answer:
    Julia Louis-Dreyfus, a decorated figure in television history, joins Sean Evans on Hot Ones to talk about her new film, You Hurt My Feelings, and her collaboration with director Nicole Holofcener. She also discusses her love for hot sauce, her college improv show, and her podcast, Wiser Than Me, where she talks to icons like Carol Burnett and Jane Fonda. 
    Actress Julia Louis-Dreyfus discusses the importance of facing fears and doing things that frighten you, as well as her experiences on the set of Seinfeld and Marvel's Wakanda Forever. She also tries spicy wings and talks about her role in Veep. 
    Julia Louis-Dreyfus appears on the YouTube show "Hot Ones" and eats progressively spicier chicken wings while answering questions. She discusses her career, living in Oakwood Apartments, and the most underrated National Park. She struggles with the spiciness of the sauces but manages to finish the challenge. 

Question (enter 'exit' to exit): exit
Session ended.
===========================================
