<div >
  <a href="https://evadb.readthedocs.io/">
    <img src="https://raw.githubusercontent.com/georgia-tech-db/eva/master/docs/images/eva/eva-banner.png" alt="EVA" width="1000px" margin-left="-5px">
  </a>
  <div>
        <h3>Try It Out!</h3>
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

EVA is an open-source **AI-relational database with first-class support for deep learning models**. It aims to support AI-powered database applications that operate on both structured (tables) and unstructured data (videos, text, podcasts, PDFs, etc.) with deep learning models.

EVA accelerates AI pipelines using a collection of optimizations inspired by relational database systems including function caching, sampling, and cost-based operator reordering. It comes with a wide range of models for analyzing unstructured data including image classification, object detection, OCR, face detection, etc. It is fully implemented in Python, and licensed under the Apache license.

EVA supports a AI-oriented query language for analysing unstructured data. Here are some illustrative applications:

 * <a href="https://evadb.readthedocs.io/en/stable/source/tutorials/03-emotion-analysis.html">Examining the emotion palette of actors in a movie</a>
 * <a href="https://evadb.readthedocs.io/en/stable/source/tutorials/02-object-detection.html">Analysing traffic flow at an intersection </a>
 * <a href="https://evadb.readthedocs.io/en/stable/source/tutorials/01-mnist.html">Classifying images based on their content</a>
 * <a href="https://github.com/georgia-tech-db/license-plate-recognition">Recogizing license plates </a>
 * <a href="https://github.com/georgia-tech-db/toxicity-classification">Analysing toxicity of social media memes </a>
 
If you are wondering why you might need a AI-relational database system, start with the page on <a href="https://evadb.readthedocs.io/en/stable/source/overview/video.html#">Video Database Systems</a>. It describes how EVA lets you easily make use of deep learning models and you can save money spent on inference on large image or video datasets.

The <a href="https://evadb.readthedocs.io/en/stable/source/overview/installation.html">Getting Started</a> page shows how you can use EVA for different computer vision tasks: image classification, object detection, action recognition, and how you can easily extend EVA to support your custom deep learning model in the form of user-defined functions.

The <a href="https://evadb.readthedocs.io/en/stable/source/tutorials/index.html">User Guides</a> section contains Jupyter Notebooks that demonstrate how to use various features of EVA. Each notebook includes a link to Google Colab, where you can run the code by yourself.

## Why EVA? ##

<details>
  <summary><b>Easily combine SQL and Deep Learning to build next-generation database applications</b></summary>
  Easily query videos in user-facing applications with a SQL-like interface for commonly used computer vision models.
</details>

<details>
  <summary><b>Speed up queries and save money spent on model inference</b></summary>
  EVA comes with a collection of built-in sampling, caching, and filtering optimizations inspired by time-tested relational database systems.
</details>

<details>
  <summary><b>Extensible by design to support custom deep learning models </b></summary>
  EVA has first-class support for user-defined functions that wrap around your deep learning models in PyTorch.
</details>

## Links
* [Documentation](https://evadb.readthedocs.io/)
* [Tutorials](https://github.com/georgia-tech-db/eva/blob/master/tutorials/03-emotion-analysis.ipynb)
* [Join Slack](https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg)
* [Demo](https://ada-00.cc.gatech.edu/eva/playground)

## Quick Start

1. To install EVA, we recommend using the pip package manager (EVA supports Python versions 3.7+).

```shell
pip install evadb
```

2. EVA is based on a client-server architecture. It works in Jupyter notebooks (illustrative notebooks are available in the [Tutorials](https://github.com/georgia-tech-db/eva/blob/master/tutorials/03-emotion-analysis.ipynb) folder) and also supports a terminal-based client. To start the EVA server and a terminal-based client, use the following commands:
```shell
eva_server &   # launch server
eva_client     # launch client
```

3. Load a video onto the EVA server from the client (we use [ua_detrac.mp4](data/ua_detrac/ua_detrac.mp4) video as an example):

```mysql
LOAD VIDEO "data/ua_detrac/ua_detrac.mp4" INTO MyVideo;
```

4. That's it! You can now run queries over the loaded video:

```mysql
SELECT id, data FROM MyVideo WHERE id < 5;
```

5. Search for frames in the video that contain a car

```mysql
SELECT id, data FROM MyVideo WHERE ['car'] <@ FastRCNNObjectDetector(data).labels;
```
| Source Video  | Query Result |
|---------------|--------------|
|<img alt="Source Video" src="https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/traffic-input.webp" width="300"> |<img alt="Query Result" src="https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/traffic-output.webp" width="300"> |

6. Search for frames in the video that contain a pedestrian and a car

```mysql
SELECT id, data FROM MyVideo WHERE ['pedestrian', 'car'] <@ FastRCNNObjectDetector(data).labels;
```

7. Search for frames in the video with more than 3 cars

```mysql
SELECT id, data FROM MyVideo WHERE ArrayCount(FastRCNNObjectDetector(data).labels, 'car') > 3;
```

8. You can create a new user-defined function (UDF) that wraps around your custom vision model or an off-the-shelf model like FastRCNN:
```mysql
CREATE UDF IF NOT EXISTS MyUDF
INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
OUTPUT (labels NDARRAY STR(ANYDIM), bboxes NDARRAY FLOAT32(ANYDIM, 4),
        scores NDARRAY FLOAT32(ANYDIM))
TYPE  Classification
IMPL  'eva/udfs/fastrcnn_object_detector.py';
```

9. You can combine multiple user-defined functions in a single query to accomplish more complicated tasks.
```mysql
   -- Analyse emotions of faces in a video
   SELECT id, bbox, EmotionDetector(Crop(data, bbox)) 
   FROM MyVideo JOIN LATERAL UNNEST(FaceDetector(data)) AS Face(bbox, conf)  
   WHERE id < 15;
```

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

We welcome all kinds of contributions to EVA.
To file a bug or request a feature, please use <a href="https://github.com/georgia-tech-db/eva/issues">GitHub issues</a>. <a href="https://github.com/georgia-tech-db/eva/pulls">Pull requests</a> are welcome.

For more information on contributing to EVA, see our
[contribution guide](https://evadb.readthedocs.io/en/stable/source/contribute/index.html).

## License
Copyright (c) 2018-2023 [Georgia Tech Database Group](http://db.cc.gatech.edu/)
Licensed under [Apache License](LICENSE).
