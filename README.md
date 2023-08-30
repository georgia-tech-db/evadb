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

The high-level SQL and Python APIs allow beginners to use EvaDB in a few lines of code. Advanced users can define custom functions that wrap around any AI model or Python library. EvaDB is fully implemented in Python and licensed under an Apache license.

## Quick Links

- [Features](#features)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Community and Support](#community-and-support)
- [Twitter](https://twitter.com/evadb_ai)

## Features

- 🔮 Build simpler AI-powered apps using SQL queries or Python functions
- ⚡️ 10x faster applications using AI-centric query optimization
- 💰 Save money spent on inference
- 🚀 First-class support for custom deep learning models through user-defined functions
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

You can find the complete documentation of EvaDB at [https://evadb.readthedocs.io/](https://evadb.readthedocs.io/).

## How does EvaDB work?

* Connect EvaDB to your data platform with the USE statement.
* Write SQL queries with AI functions to get inference results:
   - Pick a pre-trained AI model from Hugging Face, OpenAI, YOLO, PyTorch etc. for generative AI, NLP, and vision applications;
   - or pick from a variety of state-of-the-art AI engines for classic ML use-cases (classification, regression, etc.);
   - or bring your custom model built with any AI framework using CREATE FUNCTION.
* FINETUNE your AI models to achieve better results.

Follow the [getting started](https://evadb.readthedocs.io/en/stable/source/overview/getting-started.html) guide with sample data to get on-boarded as fast as possible.

## Illustrative Queries

* Call the MNIST Image Classification model to obtain digit labels for each frame in the video.

```sql
SELECT MnistImageClassifier(data).label FROM mnist_video;
```

* Build a vector index on the feature embeddings returned by the SIFT Feature Extractor on a collection of images.

```sql
CREATE INDEX reddit_sift_image_index
    ON reddit_dataset (SiftFeatureExtractor(data))
    USING FAISS
```

* Retrieve the top 5 most similar images for given image.

```sql
SELECT name FROM reddit_dataset ORDER BY
    Similarity(
        SiftFeatureExtractor(Open('reddit-images/g1074_d4mxztt.jpg')),
        SiftFeatureExtractor(data)
    )
    LIMIT 5
```

* Store the text returned by a Speech Recognition model on the audio component of a video in a table.

```sql
CREATE TABLE text_summary AS
    SELECT SpeechRecognizer(audio) FROM ukraine_video;
```

* Run ChatGPT on the text column

```sql
SELECT ChatGPT('Is this video summary related to Ukraine russia war', text)
    FROM text_summary;
```

## Architecture of EvaDB

This diagram presents the key components of EvaDB. EvaDB's AI-centric query optimizer takes a query as input and generates a query plan that is executed by the query engine. The query engine hits the relevant storage engines to quickly retrieve the data required for efficiently running the query:
1. Structured data (Tables in a SQL database system)
2. Unstructured media data (PDFs, videos, etc. on cloud/local filesystem)
3. Feature embeddings (Vector database system)

<img width="500" alt="Architecture Diagram" src="https://github.com/georgia-tech-db/evadb/assets/5521975/01452ec9-87d9-4d27-90b2-c0b1ab29b16c">

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
    <img src="https://api.star-history.com/svg?repos=georgia-tech-db/evadb&type=Date" alt="EvaDB Star History Chart" width="600">
</a>

## License
Copyright (c) 2018--present [Georgia Tech Database Group](http://db.cc.gatech.edu/).
Licensed under [Apache License](LICENSE).
