# YouTube Question Answering

## Overview
This app lets you ask questions about any YouTube video, and will only need to supply a Youtube URL and an OpenAI API key.
Additionally, you can ask the app to generate a well-formatted blog of the video for you.

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
🔮 Welcome to EvaDB! This app lets you ask questions on any local or YouTube online video.
You will only need to supply a Youtube URL and an OpenAI API key.

📹 Are you querying an online Youtube video or a local video? ('yes' for online/ 'no' for local): yes
📺 Enter the URL of the YouTube video (press Enter to use our default Youtube video URL): https://www.youtube.com/watch?v=pmqtd7CSC60
🔑 Enter your OpenAI key: [your openai api key]
⏳ Transcript download in progress...
✅ Video transcript downloaded successfully.
\===========================================
🪄 Ask anything about the video!
Question (enter 'exit' to exit): what is the video trying to show
⏳ Generating response (may take a while)...
\+--------------------------------------------------+
✅ Answer:
The video is reporting on the recent approval of a bill by lawmakers in the House to raise the US debt limit, which would avoid a potential economic catastrophe if the government were to default on its bills. The bill would restrict some spending for the next two years, suspend the debt ceiling into early 2025, cap some federal spending, eliminate funding increases for the IRS, tighten eligibility for food stamp programs, and loosen some environmental restrictions. However, the bill still needs to pass the Senate and be signed by President Biden before it becomes law. The video also highlights potential challenges in the Senate, including a controversial natural gas pipeline provision and opposition from some members. The clock is ticking as the potential default date of June 5th approaches.
\+--------------------------------------------------+
Question (enter 'exit' to exit): exit

Would you like to generate a blog post based on the video? (yes/no): yes
⏳ Generating blog post (may take a while)...
# Lawmakers Approve Bill to Raise US Debt Limit

On May 19th, lawmakers in the House approved a bill to raise the US debt limit, which would avoid an economic catastrophe if the government were to default on its bills. The bill would restrict some spending for the next two years and suspend the debt ceiling into early 2025. 

## What is the Debt Limit?

The debt limit is the maximum amount of money that the US government can borrow to pay its bills. It is set by Congress and has been raised many times over the years. If the debt limit is not raised, the government will not be able to pay its bills, which could lead to a default on its debt obligations. This would have serious consequences for the US economy and the global financial system.

## What Does the Bill Include?

The bill includes several provisions that would affect federal spending and programs. Some of the key provisions include:

- Restricting some spending for the next two years
- Suspending the debt ceiling into early 2025
- Capping some federal spending
- Eliminating funding increases for the IRS
- Tightening eligibility for food stamp programs
- Loosening some environmental restrictions

## What Happens Next?

The bill still needs to pass the Senate before being signed by President Biden. However, there are indications that some members of the Senate may put up a fight. The potential default date is still coming on June 5th, so time is running out for Congress to act.

## Conclusion

Raising the debt limit is a critical step to ensure that the US government can continue to pay its bills and avoid a default on its debt obligations. The bill passed by the House includes several provisions that would affect federal spending and programs, and it remains to be seen whether the Senate will approve the bill before the June 5th deadline. 

Sources:
- [CNN](https://www.cnn.com/2021/05/19/politics/house-debt-ceiling-vote/index.html)
- [CNBC](https://www.cnbc.com/2021/05/19/house-passes-bill-to-suspend-debt-ceiling-into-2023.html)
✅ blog post is saved to file blog.md
✅ Session ended.
===========================================
