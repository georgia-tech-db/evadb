# EvaDB: Database System for AI Apps


<p align="center">
  <a href="https://evadb.readthedocs.io">
    <img src="https://raw.githubusercontent.com/georgia-tech-db/evadb/master/docs/images/evadb/evadb-full-logo.svg" width="500" alt="EvaDB">
  </a>
</p>

#

<div align="center">
        <a href="https://colab.research.google.com/github/georgia-tech-db/evadb/blob/master/tutorials/03-emotion-analysis.ipynb">
            <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Check out EvaDB on Colab"/>
        </a>
        <a href="https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg">
            <img alt="Slack" src="https://img.shields.io/badge/slack-evadb-ff69b4.svg?logo=slack">
        </a>          
        <a href="https://twitter.com/evadb_ai">
            <img alt="Twitter" src="https://img.shields.io/badge/twitter-evadb-bde1ee.svg?logo=twitter">
        </a>  
        <a href="https://github.com/orgs/georgia-tech-db/projects/3">
            <img src="https://img.shields.io/badge/evadb-roadmap-a6c096" alt="Roadmap"/>
        </a>
        <br>
        <img alt="PyPI" src="https://img.shields.io/pypi/v/evadb.svg"/>
        <img alt="License" src="https://img.shields.io/badge/license-Apache%202-brightgreen.svg?logo=apache"/>
        <img alt="Coverage Status" src="https://coveralls.io/repos/github/georgia-tech-db/eva/badge.svg?branch=master"/>     
<!--         <a href="https://pepy.tech/project/evadb">
          <img alt="Downloads" src="https://static.pepy.tech/badge/evadb"/>
        </a> -->
        <img alt="Python Versions" src="https://img.shields.io/badge/Python--versions-3.8%20|%203.9%20|%203.10|%203.11-brightgreen"/>       
</div>

<p align="center"> <b><h3>EvaDB is a database system for building simpler and faster AI-powered applications.</b></h3> </p>

EvaDB is a database system for developing AI apps. We aim to simplify the development and deployment of AI apps that operate on unstructured data (text documents, videos, PDFs, podcasts, etc.) and structured data (tables, vector index).

The high-level Python and SQL APIs allow beginners to use EvaDB in a few lines of code. Advanced users can define custom user-defined functions that wrap around any AI model or Python library. EvaDB is fully implemented in Python and licensed under an Apache license.

## Quick Links

- [Features](#features)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Community and Support](#community-and-support)
- [Twitter](https://twitter.com/evadb_ai)

## Features

- 🔮 Build simpler AI-powered apps using Python functions or SQL queries
- ⚡️ 10x faster applications using AI-centric query optimization  
- 💰 Save money spent on inference
- 🚀 First-class support for your custom deep learning models through user-defined functions
- 📦 Built-in caching to eliminate redundant model invocations across queries
- ⌨️ Integrations for PyTorch, Hugging Face, YOLO, and Open AI models
- 🐍 Installable via pip and fully implemented in Python

## Illustrative Applications

Here are some illustrative AI apps built using EvaDB (each notebook can be opened on Google Colab):

 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/usecases/13-privategpt.html">PrivateGPT</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/usecases/08-chatgpt.html">ChatGPT-based Video Question Answering</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/usecases/12-query-pdf.html">Querying PDF Documents</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/usecases/02-object-detection.html">Analysing Traffic Flow with YOLO</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/usecases/03-emotion-analysis.html">Examining Emotions of Movie</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/usecases/07-object-segmentation-huggingface.html">Image Segmentation with Hugging Face</a>

## Documentation

* [Documentation](https://evadb.readthedocs.io/)
  - The <a href="https://evadb.readthedocs.io/en/stable/source/overview/installation.html">Getting Started</a> page shows how you can use EvaDB for different AI tasks and how you can easily extend EvaDB to support your custom deep learning model through user-defined functions.
  - The <a href="https://evadb.readthedocs.io/en/stable/source/tutorials/13-privategpt.html">User Guides</a> section contains Jupyter Notebooks that demonstrate how to use various features of EvaDB. Each notebook includes a link to Google Colab, where you can run the code yourself.
* [Join us on Slack](https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg)
* [Follow us on Twitter](https://twitter.com/evadb_ai)
* [Roadmap](https://github.com/orgs/georgia-tech-db/projects/3)

## Quick Start

- Step 1: Install EvaDB using `pip`. EvaDB supports Python versions >= `3.8`:

```shell
pip install evadb
```

- Step 2: It's time to write an AI app.

```python
import evadb

# Grab a EvaDB cursor to load data into tables and run AI queries
cursor = evadb.connect().cursor()

# Load a collection of news videos into the 'news_videos' table
# This function returns a Pandas dataframe with the query's output
# In this case, the output dataframe indicates the number of loaded videos
cursor.load(
    file_regex="news_videos/*.mp4",
    format="VIDEO",
    table_name="news_videos"
).df()

# Define a function that wraps around your deep learning model
# Here, this function wraps around a speech-to-text model
# After registering the function, we can use the registered function in subsequent queries
cursor.create_function(
    udf_name="SpeechRecognizer",
    type="HuggingFace",
    task='automatic-speech-recognition',
    model='openai/whisper-base'
).df()

# EvaDB automatically extracts the audio from the video
# We only need to run the SpeechRecongizer function on the 'audio' column
# to get the transcript and persist it in a table called 'transcripts'
cursor.query(
    """CREATE TABLE transcripts AS
       SELECT SpeechRecognizer(audio) from news_videos;"""
).df()

# We next incrementally construct the ChatGPT query using EvaDB's Python API
# The query is based on the 'transcripts' table
# This table has a column called 'text' with the transcript text
query = cursor.table('transcripts')

# Since ChatGPT is a built-in function, we don't have to define it
# We can just directly use it in the query
# We need to set the OPENAI_KEY as an environment variable
os.environ["OPENAI_KEY"] = OPENAI_KEY
query = query.select("ChatGPT('Is this video summary related to LLMs', text)")

# Finally, we run the query to get the results as a dataframe
# You can then post-process the dataframe using other Python libraries
response = query.df()
```

- **Incrementally build an AI query that chains together multiple models**

Here is a AI query that analyses emotions of actors in an `Interstellar` movie clip using multiple PyTorch models.

```python
# Access the Interstellar movie clip table using a cursor
query = cursor.table("Interstellar")
# Get faces using a `FaceDetector` function
query = query.cross_apply("UNNEST(FaceDetector(data))", "Face(bounding_box, confidence)")
# Focus only on frames 100 through 200 in the clip
query = query.filter("id > 100 AND id < 200")
# Get the emotions of the detected faces using a `EmotionDetector` function
query = query.select("id, bbox, EmotionDetector(Crop(data, bounding_box))")

# Run the query and get the query result as a dataframe
# At each of the above steps, you can run the query and see the output
# If you are familiar with SQL, you can get the SQL query with query.sql_query()
response = query.df()
```

- **EvaDB runs AI apps 10x faster using its AI-centric query optimizer**.

  Three key built-in optimizations are:

   💾 **Caching**: EvaDB automatically caches and reuses model inference results.

   ⚡️ **Parallel Query Execution**: EvaDB runs the app in parallel on all the available hardware resources (CPUs and GPUs).

   🎯 **Model Ordering**: EvaDB optimizes the order in which models are evaluated (e.g., runs the faster, more selective model first).

## Architecture Diagram

This diagram presents the key components of EvaDB. EvaDB's AI-centric query optimizer takes a query as input and generates a query plan that is executed by the query engine. The query engine hits the relevant storage engines to quickly retrieve the data required for efficiently running the query:
1. Structured data (SQL database system connected via `sqlalchemy`).
2. Unstructured media data (PDFs, videos, etc. on cloud/local filesystem).
3. Feature data (vector database system).

<img width="500" alt="Architecture Diagram" src="https://github.com/georgia-tech-db/evadb/assets/5521975/01452ec9-87d9-4d27-90b2-c0b1ab29b16c">

## Screenshots

### 🔮 [Traffic Analysis](https://evadb.readthedocs.io/en/stable/source/tutorials/02-object-detection.html) (Object Detection Model)
| Source Video  | Query Result |
|---------------|--------------|
|<img alt="Source Video" src="https://github.com/georgia-tech-db/evadb/releases/download/v0.1.0/traffic-input.webp" width="300"> |<img alt="Query Result" src="https://github.com/georgia-tech-db/evadb/releases/download/v0.1.0/traffic-output.webp" width="300"> |

### 🔮 [PDF Question Answering](https://evadb.readthedocs.io/en/stable/source/tutorials/12-query-pdf.html) (Question Answering Model)

| App |
|-----|
|<img alt="Source Video" src="https://github.com/georgia-tech-db/evadb/releases/download/v0.1.0/pdf-qa.webp" width="400"> |

### 🔮 [MNIST Digit Recognition](https://evadb.readthedocs.io/en/stable/source/tutorials/01-mnist.html) (Image Classification Model)
| Source Video  | Query Result |
|---------------|--------------|
|<img alt="Source Video" src="https://github.com/georgia-tech-db/evadb/releases/download/v0.1.0/mnist-input.webp" width="150"> |<img alt="Query Result" src="https://github.com/georgia-tech-db/evadb/releases/download/v0.1.0/mnist-output.webp" width="150"> |

### 🔮 [Movie Emotion Analysis](https://evadb.readthedocs.io/en/stable/source/tutorials/03-emotion-analysis.html) (Face Detection + Emotion Classification Models)

| Source Video  | Query Result |
|---------------|--------------|
|<img alt="Source Video" src="https://github.com/georgia-tech-db/evadb/releases/download/v0.1.0/gangubai-input.webp" width="400"> |<img alt="Query Result" src="https://github.com/georgia-tech-db/evadb/releases/download/v0.1.0/gangubai-output.webp" width="400"> |

### 🔮 [License Plate Recognition](https://github.com/georgia-tech-db/evadb-application-template) (Plate Detection + OCR Extraction Models)

| Query Result |
|--------------|
<img alt="Query Result" src="https://github.com/georgia-tech-db/license-plate-recognition/blob/main/README_files/README_12_3.png" width="300"> |

## Community and Support

👋 If you have general questions about EvaDB, want to say hello or just follow along, please join our [Slack Community](https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg) and [follow us on Twitter](https://twitter.com/evadb_ai).

<a href="https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg">
    <img src="https://raw.githubusercontent.com/georgia-tech-db/evadb/master/docs/images/evadb/evadb-slack.png" alt="EvaDB Slack Channel" width="600">
</a>

If you run into any problems or issues, please create a Github issue.

Don't see a feature in the list? Search our issue tracker if someone has already requested it and add a comment to it explaining your use-case, or open a new issue if not. We prioritize our [roadmap](https://github.com/orgs/georgia-tech-db/projects/3) based on user feedback, so we'd love to hear from you.

## Contributing

[![PyPI Version](https://img.shields.io/pypi/v/evadb.svg)](https://pypi.org/project/evadb)
[![CI Status](https://circleci.com/gh/georgia-tech-db/evadb.svg?style=svg)](https://circleci.com/gh/georgia-tech-db/evadb)
[![Documentation Status](https://readthedocs.org/projects/evadb/badge/?version=latest)](https://evadb.readthedocs.io/en/latest/index.html)

EvaDB is the beneficiary of many [contributors](https://github.com/georgia-tech-db/evadb/graphs/contributors). All kinds of contributions to EvaDB are appreciated. To file a bug or to request a feature, please use <a href="https://github.com/georgia-tech-db/evadb/issues">GitHub issues</a>. <a href="https://github.com/georgia-tech-db/evadb/pulls">Pull requests</a> are welcome.

For more information, see our
[contribution guide](https://evadb.readthedocs.io/en/stable/source/contribute/index.html).

## Star History

<a href="https://star-history.com/#georgia-tech-db/evadb&Date">
    <img src="https://api.star-history.com/svg?repos=georgia-tech-db/evadb&type=Date" alt="EvaDB Star History Chart">
</a>

## License
Copyright (c) 2018--present [Georgia Tech Database Group](http://db.cc.gatech.edu/).
Licensed under [Apache License](LICENSE).
