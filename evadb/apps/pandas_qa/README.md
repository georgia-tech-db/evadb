# Pandas Question Answering

## Overview
This app lets you run data analytics on a Pandas dataframe like a conversation. You will only need to supply a CSV file path and an OpenAI API key.

This app is powered by EvaDB's Python API and ChatGPT. Credits to the worflow presented by [pandas-ai](https://github.com/gventuri/pandas-ai)

## Setup
Ensure that the local Python version is >= 3.8. Install the required libraries:

```bat
pip install -r requirements.txt
```

## Usage
Run script: 
```bat
python pandas_qa.py
```

## Example

```bat
🔮 Welcome to EvaDB! This app lets you to run data analytics on a csv file like in a conversational manner.
You will only need to supply a path to csv file and an OpenAI API key.

📋 Enter the csv file path (press Enter to use our default csv file): [enter]
🔑 Enter your OpenAI key: [your openai key]
Could not find image processor class in the image processor config or the model config. Loading based on pattern matching with the model's feature extractor configuration.

\===========================================
🪄 Run anything on the csv table like a conversation!
What do you want to do with the dataframe?
(enter 'exit' to exit): print out the 3 countries with the highest GDPs
⏳ Generating response (may take a while)...
\+--------------------------------------------------+
✅ Script body:
\# First, we need to sort the dataframe by GDP in descending order
sorted_df = df.sort_values(by='gdp', ascending=False)

\# Then, we can select the top 3 countries with the highest GDPs
top_3_countries = sorted_df.head(3)['country']

\# Finally, we can print out the result
print("The 3 countries with the highest GDPs are:")
for country in top_3_countries:
print(country)
\+--------------------------------------------------+
🪄 Want to run it? (y/n): y
The 3 countries with the highest GDPs are:
United States
China
Japan
✅ Session ended.
\===========================================
