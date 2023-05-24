<div >
  <a href="https://evadb.readthedocs.io/">
    <img src="https://raw.githubusercontent.com/georgia-tech-db/eva/master/docs/images/eva/eva-banner.png" alt="EVA" width="1000px" margin-left="-5px">
  </a>
</div>

# EVA AI-Relational Database System

<div>
        <a href="https://colab.research.google.com/github/georgia-tech-db/eva/blob/master/tutorials/03-emotion-analysis.ipynb">
            <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open EVA on Colab"/>
        </a>
        <a href="https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg">
            <img alt="Slack" src="https://img.shields.io/badge/slack-eva-ff69b4.svg?logo=slack">
        </a>          
        <a href="https://twitter.com/evadb_ai">
            <img alt="Twitter" src="https://img.shields.io/badge/twitter-eva-C04000.svg?logo=twitter">
        </a>  
        <img alt="PyPI" src="https://img.shields.io/pypi/v/evadb.svg"/>
        <img alt="License" src="https://img.shields.io/badge/license-Apache%202-brightgreen.svg?logo=apache"/>
        <img alt="Coverage Status" src="https://coveralls.io/repos/github/georgia-tech-db/eva/badge.svg?branch=master"/>     
        <a href="https://github.com/orgs/georgia-tech-db/projects/3">
            <img src="https://img.shields.io/badge/eva-roadmap-ff3423" alt="Roadmap"/>
        </a>
        <a href="https://pepy.tech/project/evadb">
          <img alt="Downloads" src="https://static.pepy.tech/badge/evadb/month"/>
        </a>
        <img alt="Python Versions" src="https://img.shields.io/badge/Python--versions-3.8%20|%203.9%20|%203.10-brightgreen"/>       
</div>

<p align="center"> <b><h3>EVA is a database system for building simpler and faster AI-powered applications.</b></h3> </p>

EVA is designed for supporting database applications that operate on both structured (tables, feature vectors) and unstructured data (videos, podcasts, PDFs, etc.) using deep learning models. It accelerates AI pipelines by 10-100x using a collection of optimizations inspired by time-tested relational database systems, including function caching, sampling, and cost-based predicate reordering. EVA supports an AI-oriented SQL-like query language tailored for analyzing unstructured data. It comes with a wide range of models for analyzing unstructured data, including models for object detection, question answering, OCR, text sentiment classification, face detection, etc. It is fully implemented in Python and licensed under the Apache license.

## Quick Links

- [Features](#features)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Roadmap](https://github.com/orgs/georgia-tech-db/projects/3)
- [Architecture Diagram](#architecture-diagram)
- [Demo](#demo)
- [Illustrative Applications](#illustrative-applications)
- [Community and Support](#community-and-support)
- [Twitter](https://twitter.com/evadb_ai)
- [Contributing](#contributing)
- [License](#license)

## Features

- 🔮 Build simpler AI-powered applications using short SQL-like queries
- ⚡️ 10-100x faster AI pipelines using AI-centric query optimization  
- 💰 Save money spent on GPU-driven inference
- 🚀 First-class support for your custom deep learning models through user-defined functions
- 📦 Built-in caching to eliminate redundant model invocations across queries
- ⌨️ First-class support for PyTorch and HuggingFace models
- 🐍 Installable via pip and fully implemented in Python

## Demo

Here are some illustrative EVA-backed applications (all of them are Jupyter notebooks that can be opened in Google Colab):

 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/tutorials/08-chatgpt.html">Using ChatGPT to ask questions based on videos</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/tutorials/02-object-detection.html">Analysing traffic flow at an intersection</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/tutorials/03-emotion-analysis.html">Examining the emotion palette of actors in a movie</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/tutorials/11-similarity-search-for-motif-mining.html">Image Similarity Search on Reddit [FAISS + Qdrant]</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/tutorials/01-mnist.html">Classifying images based on their content</a>
 * 🔮 <a href="https://evadb.readthedocs.io/en/stable/source/tutorials/07-object-segmentation-huggingface.html">Image Segmentation using Hugging Face</a>
 * 🔮 <a href="https://github.com/georgia-tech-db/license-plate-recognition">Recognizing license plates </a>
 * 🔮 <a href="https://github.com/georgia-tech-db/toxicity-classification">Analysing toxicity of social media memes </a>

## Documentation

* [Detailed Documentation](https://evadb.readthedocs.io/)
  - If you are wondering why you might need an AI-relational Database System, start with the page on <a href="https://evadb.readthedocs.io/en/stable/source/overview/aidb.html">AI-Relational Database Systems</a>.
  - The <a href="https://evadb.readthedocs.io/en/stable/source/overview/installation.html">Getting Started</a> page shows how you can use EVA for different AI pipelines, and how you can easily extend EVA by defining an user-defined function that wraps around your custom deep learning model.
  - The <a href="https://evadb.readthedocs.io/en/stable/source/tutorials/index.html">User Guides</a> section contains Jupyter Notebooks that demonstrate how to use various features of EVA. Each notebook includes a link to Google Colab to run the code.
* [Tutorials](https://github.com/georgia-tech-db/eva/blob/master/tutorials/03-emotion-analysis.ipynb)
* [Join us on Slack](https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg)
* [Follow us on Twitter](https://twitter.com/evadb_ai)
* [Medium-Term Roadmap](https://github.com/orgs/georgia-tech-db/projects/3)
* [Demo](https://evadb.readthedocs.io/en/stable/source/tutorials/08-chatgpt.html)

## Quick Start

- Install EVA using the pip package manager. EVA supports Python versions >= 3.7:

```shell
pip install evadb
```

- To launch and connect to an EVA server in a Jupyter notebook, check out this [illustrative emotion analysis notebook](https://github.com/georgia-tech-db/eva/blob/master/tutorials/03-emotion-analysis.ipynb):
```shell
cursor = connect_to_server()
```

- Load a video onto the EVA server (we use [ua_detrac.mp4](data/ua_detrac/ua_detrac.mp4) for illustration):

```mysql
LOAD VIDEO "data/ua_detrac/ua_detrac.mp4" INTO TrafficVideo;
```

- That's it! You can now run queries over the loaded video:

```mysql
SELECT id, data FROM TrafficVideo WHERE id < 5;
```

- Search for frames in the video that contain a car:

```mysql
SELECT id, data FROM TrafficVideo WHERE ['car'] <@ Yolo(data).labels;
```
| Source Video  | Query Result |
|---------------|--------------|
|<img alt="Source Video" src="https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/traffic-input.webp" width="300"> |<img alt="Query Result" src="https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/traffic-output.webp" width="300"> |

- Search for frames in the video that contain a pedestrian and a car:

```mysql
SELECT id, data FROM TrafficVideo WHERE ['pedestrian', 'car'] <@ Yolo(data).labels;
```

- Search for frames with more than three cars:

```mysql
SELECT id, data FROM TrafficVideo WHERE ArrayCount(Yolo(data).labels, 'car') > 3;
```

- **Use your custom deep learning model in queries** with a user-defined function (UDF):

```mysql
CREATE UDF IF NOT EXISTS Yolo
TYPE  ultralytics
'model' 'yolov8m.pt';
```

- **Compose multiple models in a single query** to set up useful AI pipelines.

```mysql
   -- Analyse emotions of faces in a video
   SELECT id, bbox, EmotionDetector(Crop(data, bbox)) 
   FROM MovieVideo JOIN LATERAL UNNEST(FaceDetector(data)) AS Face(bbox, conf)  
   WHERE id < 15;
```

- **EVA runs queries faster using its AI-centric query optimizer**. Two key optimizations are:

   💾 **Caching**: EVA automatically caches and reuses previous query results (especially model inference results), eliminating redundant computation and reducing query processing time.

   🎯 **Predicate Reordering**: EVA optimizes the order in which the query predicates are evaluated (e.g., runs the faster, more selective model first), leading to faster queries and lower inference costs.

Consider these two exploratory queries on a dataset of 🐕 images:
<img align="right" style="display:inline;" width="40%" src="https://github.com/georgia-tech-db/eva/blob/master/data/assets/eva_performance_comparison.png?raw=true"></a>

```mysql
  -- Query 1: Find all images of black-colored dogs
  SELECT id, bbox FROM dogs 
  JOIN LATERAL UNNEST(Yolo(data)) AS Obj(label, bbox, score) 
  WHERE Obj.label = 'dog' 
    AND Color(Crop(data, bbox)) = 'black'; 

  -- Query 2: Find all Great Danes that are black-colored
  SELECT id, bbox FROM dogs 
  JOIN LATERAL UNNEST(Yolo(data)) AS Obj(label, bbox, score) 
  WHERE Obj.label = 'dog' 
    AND DogBreedClassifier(Crop(data, bbox)) = 'great dane' 
    AND Color(Crop(data, bbox)) = 'black';
```

By reusing the results of the first query and reordering the predicates based on the available cached inference results, EVA runs the second query **10x faster**!

## Architecture Diagram

The following architecture diagram presents the critical components of the EVA database system. EVA's AI-centric Query Optimizer takes a parsed query as input and generates a query plan that is then executed by the Query Engine. The Query Engine hits multiple storage engines to retrieve the data required for efficiently running the query:
1. Structured data (relational database system connected via `sqlalchemy`).
2. Unstructured media data (on cloud buckets or local filesystem).
3. Vector data (vector database system).

<img width="700" alt="Architecture Diagram" src="https://github.com/georgia-tech-db/eva/assets/5521975/01452ec9-87d9-4d27-90b2-c0b1ab29b16c">

## Illustrative Applications 

### 🔮 [Traffic Analysis](https://evadb.readthedocs.io/en/stable/source/tutorials/02-object-detection.html) (Object Detection Model)
| Source Video  | Query Result |
|---------------|--------------|
|<img alt="Source Video" src="https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/traffic-input.webp" width="300"> |<img alt="Query Result" src="https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/traffic-output.webp" width="300"> |

### 🔮 [MNIST Digit Recognition](https://evadb.readthedocs.io/en/stable/source/tutorials/01-mnist.html) (Image Classification Model)
| Source Video  | Query Result |
|---------------|--------------|
|<img alt="Source Video" src="https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/mnist-input.webp" width="150"> |<img alt="Query Result" src="https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/mnist-output.webp" width="150"> |

### 🔮 [Movie Emotion Analysis](https://evadb.readthedocs.io/en/stable/source/tutorials/03-emotion-analysis.html) (Face Detection + Emotion Classification Models)

| Source Video  | Query Result |
|---------------|--------------|
|<img alt="Source Video" src="https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/gangubai-input.webp" width="400"> |<img alt="Query Result" src="https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/gangubai-output.webp" width="400"> |

### 🔮 [License Plate Recognition](https://github.com/georgia-tech-db/eva-application-template) (Plate Detection + OCR Extraction Models)

| Query Result |
|--------------|
<img alt="Query Result" src="https://github.com/georgia-tech-db/license-plate-recognition/blob/main/README_files/README_12_3.png" width="300"> |

## Community and Support

👋 If you have general questions about EVA, want to say hello or just follow along, we'd like to invite you to join our [Slack Community](https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg)and to [follow us on Twitter](https://twitter.com/evadb_ai).

<a href="https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg">              
    <img src="https://raw.githubusercontent.com/georgia-tech-db/eva/master/docs/images/eva/eva-slack.png" alt="EVA Slack Channel" width="500">
</a>

If you run into any problems or issues, please create a Github issue and we'll try our best to help.

Don't see a feature in the list? Search our issue tracker if someone has already requested it and add a comment to it explaining your use-case, or open a new issue if not. We prioritize our roadmap based on user feedback, so we'd love to hear from you.

## Contributing

[![PyPI Version](https://img.shields.io/pypi/v/evadb.svg)](https://pypi.org/project/evadb)
[![CI Status](https://circleci.com/gh/georgia-tech-db/eva.svg?style=svg)](https://circleci.com/gh/georgia-tech-db/eva)
[![Documentation Status](https://readthedocs.org/projects/evadb/badge/?version=stable)](https://evadb.readthedocs.io/en/stable/index.html)

EVA is the beneficiary of many [contributors](https://github.com/georgia-tech-db/eva/graphs/contributors). All kinds of contributions to EVA are appreciated. To file a bug or to request a feature, please use <a href="https://github.com/georgia-tech-db/eva/issues">GitHub issues</a>. <a href="https://github.com/georgia-tech-db/eva/pulls">Pull requests</a> are welcome.

For more information, see our
[contribution guide](https://evadb.readthedocs.io/en/stable/source/contribute/index.html).

## License
Copyright (c) 2018-present [Georgia Tech Database Group](http://db.cc.gatech.edu/).
Licensed under [Apache License](LICENSE).
