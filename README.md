<div >
  <a href="https://evadb.readthedocs.io/">
    <img src="https://raw.githubusercontent.com/georgia-tech-db/eva/master/docs/images/eva/eva-banner.png" alt="EVA" width="1000px" margin-left="-5px">
  </a>
  <div>
        <h3>Try It Out!</h3>
        <a href="https://github.com/georgia-tech-db/eva">
            <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/georgia-tech-db/eva/master/docs/images/eva/v1.json" alt="Logo"/>
        </a>
        <a href="https://colab.research.google.com/github/georgia-tech-db/eva/blob/master/tutorials/03-emotion-analysis.ipynb">
            <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open EVA on Colab"/>
        </a>
        <a href="https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg">
            <img alt="Slack" src="https://img.shields.io/badge/slack-eva-ff69b4.svg?logo=slack">
        </a>    
        <a href="https://github.com/georgia-tech-db/eva/discussions">
            <img alt="Discuss on Github!" src="https://img.shields.io/badge/-Discuss%20on%20Github!-blueviolet">
        </a>
        <img alt="PyPI" src="https://img.shields.io/pypi/v/evadb.svg"/>
        <img alt="License" src="https://img.shields.io/badge/license-Apache%202-brightgreen.svg?logo=apache"/>
        <img alt="Python Versions" src="https://img.shields.io/badge/Python--versions-3.7%20|%203.8%20|%203.9%20|%203.10-brightgreen"/>
    </div>
</div>

# EVA AI-Relational Database System

- ⚡️ 10-100x faster AI pipelines using SQL-like queries 
- 💰 Save money spent on GPU-driven inference
- 📦 Built-in caching to avoid re-running deep learning models across queries
- 📏 Over 20 AI-centric query optimization rules
- ⌨️ First-party integrations for PyTorch and HuggingFace models
- 🐍 Installable via pip
- 🤝 Fully implemented in Python

EVA is an open-source **AI-relational database with first-class support for deep learning models**. It supports next-generation AI-powered database applications that operate on structured (tables) and unstructured data (videos, text, podcasts, PDFs, etc.) with deep learning models.

EVA accelerates AI pipelines by 10-100x using a collection of optimizations inspired by relational database systems, including function caching, sampling, and cost-based predicate reordering. It comes with a wide range of models for analyzing unstructured data, including models for image classification, object detection, OCR, text sentiment classification, face detection, etc. It is fully implemented in Python and licensed under the Apache license.

EVA supports an AI-oriented query language tailored for analyzing unstructured data. Here are some illustrative applications:

 * <a href="https://evadb.readthedocs.io/en/stable/source/tutorials/03-emotion-analysis.html">Examining the emotion palette of actors in a movie</a>
 * <a href="https://evadb.readthedocs.io/en/stable/source/tutorials/02-object-detection.html">Analysing traffic flow at an intersection </a>
 * <a href="https://evadb.readthedocs.io/en/stable/source/tutorials/01-mnist.html">Classifying images based on their content</a>
 * <a href="https://github.com/georgia-tech-db/license-plate-recognition">Recognizing license plates </a>
 * <a href="https://github.com/georgia-tech-db/toxicity-classification">Analysing toxicity of social media memes </a>
 
If you are wondering why you might need an AI-relational database system, start with the page on <a href="https://evadb.readthedocs.io/en/stable/source/overview/video.html#">Video Database Systems</a>. It describes how EVA lets you easily use deep learning models and save money spent on GPU-driven inference on large image or video datasets.

The <a href="https://evadb.readthedocs.io/en/stable/source/overview/installation.html">Getting Started</a> page shows how you can use EVA for different computer vision tasks: image classification, object detection, action recognition, and how you can easily extend EVA to support your custom deep learning model in the form of user-defined functions.

The <a href="https://evadb.readthedocs.io/en/stable/source/tutorials/index.html">User Guides</a> section contains Jupyter Notebooks that demonstrate how to use various features of EVA. Each notebook includes a link to Google Colab to run the code.

## Why EVA? ##

<details>
  <summary><b>Easily combine SQL and Deep Learning to build next-generation database applications</b></summary>
  Easily query videos in user-facing applications with a SQL-like interface for commonly used computer vision models.
</details>

<details>
  <summary><b>Speed up queries and save money spent on model inference</b></summary>
  EVA has built-in sampling, caching, and filtering optimizations inspired by time-tested relational database systems.
</details>

<details>
  <summary><b>Extensible by design to support custom deep learning models </b></summary>
  EVA has first-class support for user-defined functions that wrap around your deep learning models in PyTorch and HuggingFace.
</details>

## Links
* [Documentation](https://evadb.readthedocs.io/)
* [Tutorials](https://github.com/georgia-tech-db/eva/blob/master/tutorials/03-emotion-analysis.ipynb)
* [Join Slack](https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg)
* [Demo](https://ada-00.cc.gatech.edu/eva/playground)

## Quick Start

- Install EVA using the pip package manager. EVA supports Python versions 3.7+.

```shell
pip install evadb
```

- To start and connect to an EVA server in a Jupyter notebook, check out this [illustrative emotion analysis notebook](https://github.com/georgia-tech-db/eva/blob/master/tutorials/03-emotion-analysis.ipynb):
```shell
cursor = connect_to_server()
```

- Load a video onto the EVA server (we use [ua_detrac.mp4](data/ua_detrac/ua_detrac.mp4) for illustration):

```mysql
LOAD VIDEO "data/ua_detrac/ua_detrac.mp4" INTO UADETRAC;
```

- That's it! You can now run queries over the loaded video:

```mysql
SELECT id, data FROM UADETRAC WHERE id < 5;
```

- Search for frames in the video that contain a car

```mysql
SELECT id, data FROM UADETRAC WHERE ['car'] <@ YoloV5(data).labels;
```
| Source Video  | Query Result |
|---------------|--------------|
|<img alt="Source Video" src="https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/traffic-input.webp" width="300"> |<img alt="Query Result" src="https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/traffic-output.webp" width="300"> |

- Search for frames in the video that contain a pedestrian and a car

```mysql
SELECT id, data FROM UADETRAC WHERE ['pedestrian', 'car'] <@ YoloV5(data).labels;
```

- Search for frames with more than three cars

```mysql
SELECT id, data FROM UADETRAC WHERE ArrayCount(YoloV5(data).labels, 'car') > 3;
```

- You can **create a custom user-defined function (UDF)** that wraps around a fine-tuned or off-the-shelf deep learning model:
```mysql
CREATE UDF IF NOT EXISTS MyUDF
INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
OUTPUT (labels NDARRAY STR(ANYDIM), bboxes NDARRAY FLOAT32(ANYDIM, 4),
        scores NDARRAY FLOAT32(ANYDIM))
TYPE  Classification
IMPL  'eva/udfs/fastrcnn_object_detector.py';
```

- **Compose multiple user-defined functions in a single query** to accomplish complicated AI pipelines.
```mysql
   -- Analyse emotions of faces in a video
   SELECT id, bbox, EmotionDetector(Crop(data, bbox)) 
   FROM MyVideo JOIN LATERAL UNNEST(FaceDetector(data)) AS Face(bbox, conf)  
   WHERE id < 15;
```

- Besides making it easy to write queries for complex AI pipelines, EVA **speeds up query execution using its AI-centric query optimizer**. Two illustrative  optimizations are:

   💾 **Caching**: EVA automatically caches and reuses previous query results (especially model inference results), eliminating redundant computation and reducing query processing time.

   🎯 **Predicate Reordering**: EVA optimizes the order in which the query predicates are evaluated (e.g., runs the faster, more selective model first), leading to faster queries and lower inference costs.

Consider these two exploratory queries on a dataset of dog images:
<img align="right" style="display:inline;" width="40%" src="https://github.com/georgia-tech-db/eva/blob/master/data/assets/eva_performance_comparison.png?raw=true"></a>

```mysql
  -- Query 1: Find all images of black-colored dogs
  SELECT id, bbox FROM dogs 
  JOIN LATERAL UNNEST(YoloV5(data)) AS Obj(label, bbox, score) 
  WHERE Obj.label = 'dog' 
    AND Color(Crop(data, bbox)) = 'black'; 

  -- Query 2: Find all Great Danes that are black-colored
  SELECT id, bbox FROM dogs 
  JOIN LATERAL UNNEST(YoloV5(data)) AS Obj(label, bbox, score) 
  WHERE Obj.label = 'dog' 
    AND DogBreedClassifier(Crop(data, bbox)) = 'great dane' 
    AND Color(Crop(data, bbox)) = 'black';
```

By reusing the results of the first query and reordering the predicates based on available cached results, EVA runs up the second query **10x faster**!

## Illustrative EVA Applications 

### Traffic Analysis (Object Detection Model)
| Source Video  | Query Result |
|---------------|--------------|
|<img alt="Source Video" src="https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/traffic-input.webp" width="300"> |<img alt="Query Result" src="https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/traffic-output.webp" width="300"> |

### MNIST Digit Recognition (Image Classification Model)
| Source Video  | Query Result |
|---------------|--------------|
|<img alt="Source Video" src="https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/mnist-input.webp" width="150"> |<img alt="Query Result" src="https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/mnist-output.webp" width="150"> |

### Movie Analysis (Face Detection + Emotion Classfication Models)

| Source Video  | Query Result |
|---------------|--------------|
|<img alt="Source Video" src="https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/gangubai-input.webp" width="400"> |<img alt="Query Result" src="https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/gangubai-output.webp" width="400"> |

### [License Plate Recognition](https://github.com/georgia-tech-db/eva-application-template) (Plate Detection + OCR Extraction Models)

| Query Result |
|--------------|
<img alt="Query Result" src="https://github.com/georgia-tech-db/license-plate-recognition/blob/main/README_files/README_12_3.png" width="300"> |

### [Meme Toxicity Classification](https://github.com/georgia-tech-db/toxicity-classification) (OCR Extraction + Toxicity Classification Models)

| Query Result |
|--------------|
<img alt="Query Result" src="https://raw.githubusercontent.com/georgia-tech-db/toxicity-classification/main/README_files/README_16_2.png" width="200"> |

## Community

Join the EVA community on [Slack](https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg) to ask questions and to share your ideas for improving EVA.

<a href="https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg">              
    <img src="https://raw.githubusercontent.com/georgia-tech-db/eva/master/docs/images/eva/eva-slack.png" alt="EVA Slack Channel" width="500">
</a>

### Architecture Diagram of EVA

<img src="https://raw.githubusercontent.com/georgia-tech-db/eva/master/docs/images/eva/eva-arch.png" alt="EVA Architecture Diagram" width="500">

## Contributing to EVA

[![PyPI Version](https://img.shields.io/pypi/v/evadb.svg)](https://pypi.org/project/evadb)
[![CI Status](https://circleci.com/gh/georgia-tech-db/eva.svg?style=svg)](https://circleci.com/gh/georgia-tech-db/eva)
[![Coverage Status](https://coveralls.io/repos/github/georgia-tech-db/eva/badge.svg?branch=master)](https://coveralls.io/github/georgia-tech-db/eva?branch=master)
[![Documentation Status](https://readthedocs.org/projects/evadb/badge/?version=stable)](https://evadb.readthedocs.io/en/stable/index.html)

EVA is the beneficiary of many [contributors](https://github.com/georgia-tech-db/eva/graphs/contributors). All kinds of contributions to EVA are appreciated. To file a bug or to request a feature, please use <a href="https://github.com/georgia-tech-db/eva/issues">GitHub issues</a>. <a href="https://github.com/georgia-tech-db/eva/pulls">Pull requests</a> are welcome.

For more information, see our
[contribution guide](https://evadb.readthedocs.io/en/stable/source/contribute/index.html).

## License
Copyright (c) 2018-2023 [Georgia Tech Database Group](http://db.cc.gatech.edu/).
Licensed under [Apache License](LICENSE).
