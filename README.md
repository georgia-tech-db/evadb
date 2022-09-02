<div align="center" style="display:flex;flex-direction:column;">
  <a href="https://georgia-tech-db.github.io/eva/index.html">
    <img src="https://raw.githubusercontent.com/georgia-tech-db/eva/master/docs/Logo.png" alt="EVA" width="600px" margin-left="-5px">
  </a>
  <h3>Quickly capture information embedded in videos!</h3>
  <p>
  </p>
  <p>
</div>

<div align="center" style="display:flex;flex-direction:column;">
    <h3>🌟 Try It Out! 🌟</h3>
    <div>
        <a href="https://colab.research.google.com/drive/1H0HNOoCqvO5RFr0ousWku6YJK3qeApCN#scrollTo=B4gcnpDu5q4n">
            <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab"/>
        </a>
        <a href="https://github.com/georgia-tech-db/eva/discussions">
            <img alt="Discuss on Github!" src="https://img.shields.io/badge/-Discuss%20on%20Github!-blueviolet">
        </a>
    </div>
</div>

# EVA Video Analytics System

[![PyPI Status](https://img.shields.io/pypi/v/evadb.svg)](https://pypi.org/project/evadb)
[![CI Status](https://circleci.com/gh/georgia-tech-db/eva.svg?style=svg)](https://circleci.com/gh/georgia-tech-db/eva)
[![Coverage Status](https://coveralls.io/repos/github/georgia-tech-db/eva/badge.svg?branch=master)](https://coveralls.io/github/georgia-tech-db/eva?branch=master)
[![License](https://img.shields.io/badge/license-Apache%202-brightgreen.svg?logo=apache)](https://github.com/georgia-tech-db/eva/blob/master/LICENSE.txt)
[![Documentation Status](https://readthedocs.org/projects/exvian/badge/?version=latest)](https://evadb.readthedocs.io/en/latest/index.html)
[![Discuss](https://img.shields.io/badge/-Discuss!-blueviolet)](https://github.com/georgia-tech-db/eva/discussions)
![Python Versions](https://img.shields.io/badge/Python--versions-3.7+-brightgreen)

## What is EVA?

EVA is a new database system tailored for video analytics -- think MySQL for videos. It supports a simple SQL-like language for querying videos (e.g., finding frames in a movie with your favorite actor or find touchdowns in a football game). It comes with a wide range of commonly used computer vision models.

## Why EVA? ##

👀 Easily query videos in user-facing applications with a simple SQL-like interface for commonly used computer vision models.

🚅 Speed up queries and save money spent on model inference using in-built sampling, caching, and filtering optimizations.

✨ Hit your target accuracy using state-of-the-art model selection and query optimization algorithms.

## Links
* [Quick Demo](https://ada-00.cc.gatech.edu/eva/playground)
* [Documentation](https://evadb.readthedocs.io/en/latest/)
* [Tutorials](https://github.com/georgia-tech-db/eva/tree/master/tutorials)
* [Website](https://georgia-tech-db.github.io/eva/index.html)

## QuickStart

1. EVA requires Python 3.7+. To install EVA, we recommend using an virtual environment and the pip package manager:

```shell
pip install evadb
```

1. Start the EVA server and the client programs
```shell
eva_server&   # launch server
eva_client    # launch client
```

2. UPLOAD a video using the client (we use [ua_detrac.mp4](data/ua_detrac/ua_detrac.mp4) video as an example):

```mysql
UPLOAD INFILE 'data/ua_detrac/ua_detrac.mp4' PATH 'test_video.mp4';
```

3. LOAD the video using the following command:

```mysql
LOAD FILE 'test_video.mp4' INTO MyVideo;
```

4. That's it. You can now start issuing queries over the loaded video:

```mysql
SELECT id, data FROM MyVideo WHERE id < 5;
```

## More Interesting Queries

1. Search for frames in the video that contain a car

```mysql
SELECT id, data FROM MyVideo WHERE ['car'] <@ FastRCNNObjectDetector(data).labels;
```
![QueryResult](https://georgia-tech-db.github.io/eva/Img/car.gif)

2. Search for frames in the video that contain a pedestrian and a car

```mysql
SELECT id, data FROM MyVideo WHERE ['pedestrian', 'car'] <@ FastRCNNObjectDetector(data).labels;
```

3. Search for frames in the video with more than 3 cars

```mysql
SELECT id, data FROM MyVideo WHERE Array_Count(FastRCNNObjectDetector(data).labels, 'car') > 3;
```

4. Create your own user-defined function (UDF) that wraps around a vision model like FastRCNN
```mysql
CREATE UDF IF NOT EXISTS MyUDF
INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
OUTPUT (labels NDARRAY STR(ANYDIM), bboxes NDARRAY FLOAT32(ANYDIM, 4),
        scores NDARRAY FLOAT32(ANYDIM))
TYPE  Classification
IMPL  'eva/udfs/fastrcnn_object_detector.py';
```

## Contributing to EVA

### Development Environment Setup

To install EVA from source, use a virtual environment and the pip package manager. EVA requires JAVA 8 for generating the parser.

```shell
git clone https://github.com/georgia-tech-db/eva.git && cd eva
python3 -m venv test_eva_db                             # to create a virtual environment
source test_eva_db/bin/activate                         # activate virtual environment
pip install --upgrade pip
sudo -E apt install -y openjdk-11-jdk openjdk-11-jre    # to install JAVA
sh script/antlr4/generate_parser.sh                     # to generate the EVA parser
pip install -e ".[dev]"
```

Note: If you face Pytorch CUDA compatibility issues after installation, refer this [link](https://pytorch.org/get-started/previous-versions/) and re-install the correct `torch` and `torchvision` packages with `pip` 

To verify that installation is successful, run the test suite.

```shell
sh script/test/test.sh
```

### Contributing Guidelines

To file a bug or request a feature, please use GitHub issues. Pull requests are welcome.
For more information on installing from source, troublshooting,and contributing to EVA, see our
[contributing guidelines](https://evadb.readthedocs.io/en/latest/source/contribute/index.html).

## Contributors

See the [people page](https://github.com/georgia-tech-db/eva/graphs/contributors) for the full listing of contributors.

## License
Copyright (c) 2018-2022 [Georgia Tech Database Group](http://db.cc.gatech.edu/)
Licensed under [Apache License](LICENSE).
