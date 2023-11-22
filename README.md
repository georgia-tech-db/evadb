<p align="center">
  <a href="https://evadb.readthedocs.io">
    <img src="https://raw.githubusercontent.com/georgia-tech-db/evadb/master/docs/images/evadb/evadb-full-logo.svg" width="40%" alt="EvaDB">
  </a>
</p>

<p align="center"><i><b>Database system for AI-powered apps</b></i></p>

<p align="center">
<a href="https://github.com/georgia-tech-db/evadb/fork" target="blank">
<img src="https://img.shields.io/github/forks/georgia-tech-db/evadb?style=for-the-badge" alt="EvaDB forks"/>
</a>

<a href="https://github.com/georgia-tech-db/evadb/stargazers" target="blank">
<img src="https://img.shields.io/github/stars/georgia-tech-db/evadb?style=for-the-badge" alt="EvaDB stars"/>
</a>
<a href="https://github.com/georgia-tech-db/evadb/pulls" target="blank">
<img src="https://img.shields.io/github/issues-pr/georgia-tech-db/evadb?style=for-the-badge" alt="EvaDB pull-requests"/>
</a>
<a href='https://github.com/georgia-tech-db/evadb/releases'>
<img src='https://img.shields.io/github/release/georgia-tech-db/evadb?&label=Latest&style=for-the-badge'>
</a>

<a href="https://github.com/georgia-tech-db/evadb/commits" target="blank">
<img src="https://img.shields.io/github/commits-since/georgia-tech-db/evadb/v0.1.0.svg?style=for-the-badge" alt="EvaDB Commits"/>
</a>
</p>

<p align="center"><b>Follow EvaDB</b></p>

<p align="center">
<a href="https://evadb.ai/community" target="blank">
<img src="https://img.shields.io/badge/slack-evadb-orange.svg?logo=slack" alt="Join EvaDB Slack Community"/>
</a>
<a href="https://twitter.com/evadb_ai" target="blank">
<img src="https://img.shields.io/twitter/follow/evadb_ai?label=Follow: evadb_ai&style=social" alt="Follow evadb_ai"/>
</a>
<a href="https://medium.com/evadb-blog/" target="blank">
<img src="https://img.shields.io/badge/EvaDB_Blog-Medium-8A2BE2" alt="EvaDB on Medium"/>
<a href="https://evadb.ai/" target="blank">
<img src="https://img.shields.io/website/http/www.evadb.ai" alt="EvaDB Website"/>
</a>
</p>

<p align="center">
  <a href="https://colab.research.google.com/github/georgia-tech-db/evadb/blob/master/tutorials/03-emotion-analysis.ipynb">
      <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Launch EvaDB on Colab"/>
  </a>  	
  <a href="https://github.com/orgs/georgia-tech-db/projects/3">
      <img src="https://img.shields.io/badge/evadb-roadmap-a6c096" alt="Roadmap"/>
  </a>
  <img alt="Python Versions Supported" src="https://img.shields.io/badge/Python--versions-3.8~3.11-brightgreen"/>
  <img alt="License" src="https://img.shields.io/badge/license-Apache%202-brightgreen.svg?logo=apache"/>
  <img alt="Coverage Status" src="https://coveralls.io/repos/github/georgia-tech-db/eva/badge.svg?branch=master"/>  
<!-- <a href="https://pepy.tech/project/evadb">
          <img alt="Downloads" src="https://static.pepy.tech/badge/evadb"/>
        </a> -->  
  <br />
</p>

EvaDB enables software developers to build AI apps in a few lines of code. Its powerful SQL API simplifies AI app development for both structured and unstructured data. EvaDB's benefits include:
<details>
<summary> 🔮 Easy to <a href="https://evadb.readthedocs.io/en/latest/source/overview/connect-to-data-sources.html">connect the EvaDB query engine with your data sources</a>, such as PostgreSQL or S3 buckets, and build AI-powered apps with SQL queries. </summary>
<br/>
<table>
<tr>
<th>Structured Data Sources</th>
<th>Unstructured Data Sources</th>
<th>Application Data Sources</th>
</tr>
<tr>
<td>

- PostgreSQL
- SQLite
- MySQL
- MariaDB
- Clickhouse
- Snowflake

</td>
<td>

- Local filesystem
- AWS S3 bucket

</td>
<td>

- Github

</td>
</tr>
</table>

More details on the supported data sources is [available here](https://evadb.readthedocs.io/en/latest/source/reference/databases/index.html).

</details>

<details>
<summary> 🤝 <a href="https://evadb.readthedocs.io/en/latest/source/overview/ai-queries.html">Query your connected data with a pre-trained AI model</a> from Hugging Face, OpenAI, YOLO, Stable Diffusion, etc. </summary>
<br/>
<table>
<tr>
<th>Hugging Face</th>
<th>OpenAI</th>
<th>YOLO</th>
</tr>
<tr>
<td>

- Audio Classification
- Automatic Speech Recognition
- Text Classification
- Summarization
- Text2Text Generation
- Text Generation
- Image Classification
- Image Segmentation
- Image-to-Text
- Object Detection
- Depth Estimation

</td>
<td>

- gpt-4
- gpt-4-0314
- gpt-4-32k
- gpt-4-32k-0314
- gpt-3.5-turbo
- gpt-3.5-turbo-0301

</td>
<td>

- yolov8n.pt
- yolov8s.pt
- yolov8m.pt
- yolov8l.pt
- yolov8x.pt

</td>
</tr>
</table>

More details on the supported AI models is [available here](https://evadb.readthedocs.io/en/latest/source/reference/ai/index.html)
</details>

<details>
<summary> 🔧 Create or fine-tune AI models for regression, classification, and time series forecasting.</summary>
<br/>
<table>
<tr>
<th>Regression</th>
<th>Classification</th>
<th>Time Series Forecasting</th>
</tr>
<tr>
<td>

- Ludwig
- Sklearn
- Xgboost

</td>
<td>

- Ludwig
- Xboost

</td>
<td>

- Statsforecast
- Neuralforecast

</td>
</tr>
</table>

More details on the supported AutoML frameworks is [available here](https://evadb.readthedocs.io/en/latest/source/reference/ai/index.html).
</details>

<details>
<summary> 💰 Faster AI queries thanks to AI-centric query optimizations such as caching, batching, and parallel processing. </summary>
<br/>
  
- Function result caching helps reuse results of expensive AI function calls.
- LLM batching reduces token usage and dollars spent on LLM calls. 
- Parallel query processing saves money and time spent on running AI models by better utilizing CPUs and/or GPUs.
- Query predicate re-ordering and predicate push-down accelerates queries over both structured and unstructured data.

More details on the optimizations in EvaDB is [available here](https://evadb.readthedocs.io/en/latest/source/reference/optimizations.html).
</details>
<br/>

👋 Hey! If you're excited about our vision of bringing AI inside database systems, show some ❤️ by: 
<ul>
  <li> ⭐ starring our <a href="https://github.com/georgia-tech-db/evadb">GitHub 🐙 Repo</a>
  <li> 📟 joining our <a href="https://evadb.ai/community">Slack Community</a>
  <li> 🐦 following us on <a href="https://twitter.com/evadb_ai">Twitter</a>
  <li> 📝 following us on <a href="https://medium.com/evadb-blog">Medium</a>
</ul>

We would love to learn about your AI app. Please complete this 1-minute form: https://v0fbgcue0cm.typeform.com/to/BZHZWeZm

## Quick Links

- [Quick Links](#quick-links)
- [Documentation](#documentation)
- [Why EvaDB](#why-evadb)
- [How does EvaDB work](#how-does-evadb-work)
- [Illustrative Queries](#illustrative-queries)
- [Illustrative Apps](#illustrative-apps)
- [More Illustrative Queries](#more-illustrative-queries)
- [Architecture of EvaDB](#architecture-of-evadb)
- [Community and Support](#community-and-support)
- [Contributing](#contributing)
- [Star History](#star-history)
- [License](#license)

## Documentation

You can find the complete documentation of EvaDB at [evadb.ai/docs](https://evadb.ai/docs/) 📚✨🚀

## Why EvaDB
 
In the world of AI, we've reached a stage where many AI tasks that were traditionally handled by AI or ML engineers can now be automated. EvaDB enables software developers with the ability to perform advanced AI tasks without needing to delve into the intricate details.

EvaDB covers many AI applications, including regression, classification, image recognition, question answering, and many other generative AI applications. EvaDB targets 99% of AI problems that are often repetitive and can be automated with a simple function call in an SQL query. Until now, there is no comprehensive open-source framework for bringing AI into an existing SQL database system with a principled AI optimization framework, and that's where EvaDB comes in.

Our target audience is software developers who may not necessarily have a background in AI but require AI capabilities to solve specific problems. We target programmers who write simple SQL queries inside their CRUD apps. With EvaDB, it is possible to easily add AI features to these apps by calling built-in AI functions in the queries.

## How does EvaDB work

<details>
<ul>
<li>Connect EvaDB to your SQL and vector database systems with the <a href="https://evadb.readthedocs.io/en/stable/source/reference/databases/postgres.html">`CREATE DATABASE`</a> and <a href="https://evadb.readthedocs.io/en/stable/source/reference/evaql/create_index.html">`CREATE INDEX`</a> statements.</li>
<li>Write SQL queries with AI functions to get inference results:</li>
   <ul>
   <li>Pick a pre-trained AI model from Hugging Face, Open AI, Ultralytics, PyTorch, and built-in AI frameworks for generative AI, NLP, and vision applications;</li>  
   <li>or pick from a variety of state-of-the-art ML engines for classic ML use-cases (classification, regression, etc.);</li>
   <li>or bring your custom model built with any AI/ML framework using `CREATE FUNCTION`.</li>
   </ul>
</ul> 
  
Follow the [getting started](https://evadb.readthedocs.io/en/stable/source/overview/getting-started.html) guide to get on-boarded as fast as possible.
</details>

## Illustrative Queries

* Get insights about Github stargazers using GPT4.

```sql
SELECT name, country, email, programming_languages, social_media, GPT4(prompt,topics_of_interest)
FROM gpt4all_StargazerInsights;

--- Prompt to GPT-4
You are given 10 rows of input, each row is separated by two new line characters.
Categorize the topics listed in each row into one or more of the following 3 technical areas - Machine Learning, Databases, and Web development. If the topics listed are not related to any of these 3 areas, output a single N/A. Do not miss any input row. Do not add any additional text or numbers to your output.
The output rows must be separated by two new line characters. Each input row must generate exactly one output row. For example, the input row [Recommendation systems, Deep neural networks, Postgres] must generate only the output row [Machine Learning, Databases].
The input row [enterpreneurship, startups, venture capital] must generate the output row N/A.
```

* Build a vector index on the feature embeddings returned by the SIFT Feature Extractor on a collection of Reddit images. Return the top-5 similar images for a given image.

```sql
CREATE INDEX reddit_sift_image_index
    ON reddit_dataset (SiftFeatureExtractor(data))
    USING FAISS

SELECT name FROM reddit_dataset ORDER BY
    Similarity(
        SiftFeatureExtractor(Open('reddit-images/g1074_d4mxztt.jpg')),
        SiftFeatureExtractor(data)
    )
    LIMIT 5
```

## Illustrative Apps

Here are some illustrative AI apps built using EvaDB (each notebook can be opened on Google Colab):

 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/usecases/sentiment-analysis.html">Sentiment Analysis using LLM within PostgreSQL</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/usecases/question-answering.html">ChatGPT-based Video Question Answering</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/usecases/text-summarization.html">Text Summarization on PDF Documents</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/usecases/object-detection.html">Analysing Traffic Flow with YOLO</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/usecases/emotion-analysis.html">Examining Emotions of Movie</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/usecases/image-search.html">Image Similarity Search</a>


## More Illustrative Queries

<details>

* Get a transcript from a video stored in a table using a Speech Recognition model. Then, ask questions on the extracted transcript using ChatGPT.

```sql
CREATE TABLE text_summary AS
    SELECT SpeechRecognizer(audio) FROM ukraine_video;
SELECT ChatGPT('Is this video summary related to Ukraine russia war', text)
    FROM text_summary;
```

* Train a classic ML model for prediction using the <a href="https://ludwig.ai/latest/">Ludwig AI</a> engine.

```sql
CREATE FUNCTION IF NOT EXISTS PredictHouseRent FROM
(SELECT * FROM HomeRentals)
TYPE Ludwig
PREDICT 'rental_price'
TIME_LIMIT 120;
```

</details>

## Architecture of EvaDB

<details>	
EvaDB's AI-centric query optimizer takes a query as input and generates a query plan. The query engine takes the query plan and hits the relevant backends to efficiently process the query:
1. SQL Database Systems (Structured Data)
2. AI Frameworks (Transform Unstructured Data to Structured Data; Unstructured data includes PDFs, text, images, etc. stored locally or on the cloud)
3. Vector Database Systems (Feature Embeddings)

<p align="center">
  <img width="70%" alt="Architecture Diagram" src="https://raw.githubusercontent.com/georgia-tech-db/evadb/staging/docs/images/evadb/eva-arch-for-user.png">
</p>
</details>

## Community and Support

We would love to learn about your AI app. Please complete this 1-minute form: https://v0fbgcue0cm.typeform.com/to/BZHZWeZm

<!--<p>
  <a href="https://evadb.ai/community">
      <img width="70%" src="https://raw.githubusercontent.com/georgia-tech-db/evadb/master/docs/images/evadb/evadb-slack.png" alt="EvaDB Slack Channel">
  </a>
</p>-->

If you run into any bugs or have any comments, you can reach us on our <a href="https://evadb.ai/community">Slack Community 📟</a>  or create a [Github Issue :bug:](https://github.com/georgia-tech-db/evadb/issues). 

Here is EvaDB's public [roadmap 🛤️](https://github.com/orgs/georgia-tech-db/projects/3). We prioritize features based on user feedback, so we'd love to hear from you!

## Contributing

We are a lean team on a mission to bring AI inside database systems! All kinds of contributions to EvaDB are appreciated 🙌 If you'd like to get involved, here's information on where we could use your help: [contribution guide](https://evadb.readthedocs.io/en/latest/source/dev-guide/contribute.html) 🤗

<p align="center">
  <a href="https://github.com/georgia-tech-db/evadb/graphs/contributors">
    <img width="70%" src="https://contrib.rocks/image?repo=georgia-tech-db/evadb" />
  </a>
</p>

<details>
<b> CI Status: </b> 

[![CI Status](https://circleci.com/gh/georgia-tech-db/evadb.svg?style=svg)](https://circleci.com/gh/georgia-tech-db/evadb)
[![Documentation Status](https://readthedocs.org/projects/evadb/badge/?version=latest)](https://evadb.readthedocs.io/en/latest/index.html)
</details>

## Star History

<p align="center">
  <a href="https://star-history.com/#georgia-tech-db/evadb&Date">
      <img width="90%" src="https://api.star-history.com/svg?repos=georgia-tech-db/evadb&type=Date" alt="EvaDB Star History Chart">
  </a>
</p>

## License
Copyright (c) [Georgia Tech Database Group](http://db.cc.gatech.edu/).
Licensed under an [Apache License](LICENSE.txt).
