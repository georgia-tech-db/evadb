# EVA Video Analytics System

[![PyPI Status](https://img.shields.io/pypi/v/evadb.svg)](https://pypi.org/project/evadb)
[![CI Status](https://circleci.com/gh/georgia-tech-db/eva.svg?style=svg)](https://circleci.com/gh/georgia-tech-db/eva)
[![Coverage Status](https://coveralls.io/repos/github/georgia-tech-db/eva/badge.svg?branch=master)](https://coveralls.io/github/georgia-tech-db/eva?branch=master)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Documentation Status](https://readthedocs.org/projects/exvian/badge/?version=latest)](https://evadb.readthedocs.io/en/latest/index.html)
[![Discuss](https://img.shields.io/badge/-Discuss!-blueviolet)](https://github.com/georgia-tech-db/eva/discussions)

## What is EVA?

EVA is a video database system (think MySQL for videos). It supports a SQL-like language for querying videos (e.g., find frames in a movie with your favorite actor or find touchdowns in a football game). It supports a wide range of commonly used  computer vision models.

## Why EVA? ##

👀 EVA **enables querying of visual data** in user facing applications by providing a simple SQL-like interface for a wide range of commonly used computer vision models.

🚅 EVA **improves throughput** by introducing sampling, filtering, and caching techniques.

✨ EVA **improves accuracy** by introducing state-of-the-art model specialization and selection algorithms.

## Links
* [Quick Demo](https://ada-00.cc.gatech.edu/eva/playground)
* [Documentation](https://evadb.readthedocs.io/en/latest/)
* [Tutorials](https://github.com/georgia-tech-db/eva/tree/master/tutorials)
* [Website](https://georgia-tech-db.github.io/eva/index.html)

## QuickStart

1. EVA requires Python 3.8+. To install EVA, we recommend using an virtual environment and the pip package manager:

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
