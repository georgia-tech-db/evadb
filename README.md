<p align="center">
  <a href="https://evadb.readthedocs.io">
    <img src="https://raw.githubusercontent.com/georgia-tech-db/evadb/master/docs/images/evadb/evadb-full-logo.svg" width="70%" alt="EvaDB">
  </a>
</p>

<p align="center">
	<a href="https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg"><img src="https://img.shields.io/badge/slack-@evadb-ff69b4.svg?logo=slack " alt="EvaDB Community"></a>
  <a href="https://twitter.com/evadb_ai">
      <img alt="Twitter" src="https://img.shields.io/badge/twitter-@evadb_ai-bde1ee.svg?logo=twitter">
  </a>   
  <img alt="Python Versions Supported" src="https://img.shields.io/badge/Python--versions-3.8.x%20|%203.9.x%20|%203.10.x|%203.11.x-brightgreen"/>
	<br />     
  <img alt="PyPI" src="https://img.shields.io/pypi/v/evadb.svg"/>
  <img alt="License" src="https://img.shields.io/badge/license-Apache%202-brightgreen.svg?logo=apache"/>
  <img alt="Coverage Status" src="https://coveralls.io/repos/github/georgia-tech-db/eva/badge.svg?branch=master"/>  
	<a href="https://www.evadb.ai/"><img src="https://img.shields.io/website?url=https%3A%2F%2Fwww.evadb.ai%2F" alt="EvaDB Website"></a>   
  <a href="https://github.com/orgs/georgia-tech-db/projects/3">
      <img src="https://img.shields.io/badge/evadb-roadmap-a6c096" alt="Roadmap"/>
  </a>
<!-- <a href="https://pepy.tech/project/evadb">
          <img alt="Downloads" src="https://static.pepy.tech/badge/evadb"/>
        </a> -->  
  <br />
  <a href="https://colab.research.google.com/github/georgia-tech-db/evadb/blob/master/tutorials/03-emotion-analysis.ipynb">
      <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Launch EvaDB on Colab"/>
  </a>  
  <br />
  <a href="https://gitpod.io/#https://github.com/georgia-tech-db/evadb" target="_blank"><img src="https://gitpod.io/button/open-in-gitpod.svg" alt="Open in Gitpod"></a>
</p>

## EvaDB is an AI layer on your Database System

EvaDB simplifies the development of AI apps that operate on both structured data (tables, feature vectors) and unstructured data (text, images, videos, PDFs, podcasts, etc.). 

Its powerful SQL API empowers software developers to build AI apps in a few lines of code. Developers can define custom functions that wrap around any AI model or Python library.

EvaDB offers these primary benefits:
- 🔮 Easy to connect EvaDB with a SQL database system and build AI-powered applications with a few SQL queries
- 🤝 Query your data using a pre-trained AI model from Hugging Face, OpenAI, YOLO, PyTorch, and other built-in integrations
- ⚡️ 10x faster queries using AI-centric query optimization
- 💰 Save money spent on running models by improving utilization of CPUs and GPUs
- 🔧 Fine-tune your AI models to achieve better results

👋 Hey there! If you're excited about our vision of bringing AI to database systems, please show some ❤️ by: 
  - giving a ⭐ on our [EvaDB repo on Github 🐙](https://github.com/georgia-tech-db/evadb)
  - joining our [Slack Community 📟](https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg)
  - [following us on Twitter 🐦](https://twitter.com/evadb_ai)

## Quick Links

- [Documentation](#documentation)
- [Community and Support](#community-and-support)
- [Illustrative Queries](#illustrative-queries)
- [Illustrative Apps](#illustrative-apps)

## Documentation

You can find the complete documentation of EvaDB at: [https://evadb.readthedocs.io/](https://evadb.readthedocs.io/)

## How does EvaDB work?

* Connect EvaDB to your database system with the `USE` statement.
* Write SQL queries with AI functions to get inference results:
   - Pick a pre-trained AI model from Hugging Face, OpenAI, YOLO, PyTorch etc. for generative AI, NLP, and vision applications;
   - or pick from a variety of state-of-the-art ML engines for classic ML use-cases (classification, regression, etc.);
   - or bring your custom model built with any AI/ML framework using `CREATE FUNCTION`.
* `FINETUNE` your AI models to achieve better results.

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

## Illustrative Apps

Here are some illustrative AI apps built using EvaDB (each notebook can be opened on Google Colab):

 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/usecases/13-privategpt.html">PrivateGPT</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/usecases/08-chatgpt.html">ChatGPT-based Video Question Answering</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/usecases/12-query-pdf.html">Querying PDF Documents</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/usecases/02-object-detection.html">Analysing Traffic Flow with YOLO</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/usecases/03-emotion-analysis.html">Examining Emotions of Movie</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/usecases/07-object-segmentation-huggingface.html">Image Segmentation with Hugging Face</a>

## Architecture of EvaDB

EvaDB's AI-centric query optimizer takes a query as input and generates a query plan. The query engine takes the query plan and hits the relevant backends to efficiently process the query:
1. SQL Database Systems (Structured Data)
2. AI Frameworks (Transform Unstructured Data to Structured Data, Unstructured data includes PDFs, images, podcasts, etc. stored on cloud buckets or local filesystem)
3. Vector Database Systems (Feature Embeddings)

<p align="center">
  <img width="70%" alt="Architecture Diagram" src="https://raw.githubusercontent.com/georgia-tech-db/evadb/staging/docs/images/evadb/eva-arch-for-user.png">
</p>

## Community and Support

👋 Hey there! If you're excited about our vision of bringing AI to database systems, please show some ❤️ by: 
  - giving a ⭐ on our [EvaDB repo on Github 🐙](https://github.com/georgia-tech-db/evadb)
  - joining our [Slack Community 📟](https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg)
  - [following us on Twitter 🐦](https://twitter.com/evadb_ai)

<p align="center">
  <a href="https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg">
      <img width="70%" src="https://raw.githubusercontent.com/georgia-tech-db/evadb/master/docs/images/evadb/evadb-slack.png" alt="EvaDB Slack Channel">
  </a>
</p>

If you run into any bugs or have any comments, please create a [Github Issue :bug:](https://github.com/georgia-tech-db/evadb/issues). 

Here is our [roadmap 🛤️](https://github.com/orgs/georgia-tech-db/projects/3). We prioritize features based on user feedback, so we'd love to hear from you! If you do not see a feature you are interested in the roadmap, please create a [Github Issue :bug:](https://github.com/georgia-tech-db/evadb/issues).

## Contributing

[![PyPI Version](https://img.shields.io/pypi/v/evadb.svg)](https://pypi.org/project/evadb)
[![CI Status](https://circleci.com/gh/georgia-tech-db/evadb.svg?style=svg)](https://circleci.com/gh/georgia-tech-db/evadb)
[![Documentation Status](https://readthedocs.org/projects/evadb/badge/?version=latest)](https://evadb.readthedocs.io/en/latest/index.html)

EvaDB is the beneficiary of many [contributors 🙌](https://github.com/georgia-tech-db/evadb/graphs/contributors). 

<p align="center">
  <a href="https://github.com/georgia-tech-db/evadb/graphs/contributors">
    <img width="70%" src="https://contrib.rocks/image?repo=georgia-tech-db/evadb" />
  </a>
</p>

All kinds of contributions to EvaDB are appreciated. To file a bug or to request a feature, please use <a href="https://github.com/georgia-tech-db/evadb/issues">GitHub issues</a>. <a href="https://github.com/georgia-tech-db/evadb/pulls">Pull requests</a> are welcome. For more information, see our
[contribution guide](https://evadb.readthedocs.io/en/stable/source/contribute/index.html).

## Star History

<p align="center">
  <a href="https://star-history.com/#georgia-tech-db/evadb&Date">
      <img width="90%" src="https://api.star-history.com/svg?repos=georgia-tech-db/evadb&type=Date" alt="EvaDB Star History Chart">
  </a>
</p>

## License
Copyright (c) [Georgia Tech Database Group](http://db.cc.gatech.edu/).
Licensed under an [Apache License](LICENSE).
