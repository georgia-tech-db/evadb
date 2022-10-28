> code cannot run in colab because the pip version of evadb is incompatible with the current github version in terms of udf

How to run locally 

```
git clone https://github.com/sashiko-345/eva.git && cd eva # our folked eva
python3 -m venv test_eva_db                            # to create a virtual environment
. test_eva_db/bin/activate
pip install --upgrade pip
sudo -E apt install -y openjdk-11-jdk openjdk-11-jre   # to install JAVA # may need other way to install jre 11 in mac os
sh script/antlr4/generate_parser.sh                    # to generate the EVA parser
pip install -e ".[dev]"
bash script/test/test.sh 
```

For developers using an M1 Mac, here are some pointers for installing JAVA and to resolve multi-threading issues:
```
brew install openjdk@11                         # to install openjdk 11
export JAVA_HOME="/opt/homebrew/opt/openjdk@11" # add this command in ~/.zshrc or ~/.bashrc
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES  # to resolve multi-threading issues in macOS
```
<div >
  <a href="https://georgia-tech-db.github.io/eva/index.html">
    <img src="https://raw.githubusercontent.com/georgia-tech-db/eva/master/docs/Logo.png" alt="EVA" width="300px" margin-left="-5px">
  </a>
  <h3>EVA Video Database System: Where SQL meets Deep Learning!</h3>
  <div>
        <h3>🌟 Try It Out! 🌟</h3>
        <a href="https://colab.research.google.com/github/georgia-tech-db/eva/blob/master/tutorials/02-object-detection.ipynb">
            <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open EVA on Colab"/>
        </a>
        <a href="https://github.com/georgia-tech-db/eva/discussions">
            <img alt="Discuss on Github!" src="https://img.shields.io/badge/-Discuss%20on%20Github!-blueviolet">
        </a>
    </div>
</div>

## Links
* [Documentation](https://evadb.readthedocs.io/en/latest/)
* [Tutorials](https://github.com/georgia-tech-db/eva/tree/master/tutorials)
* [Website](https://georgia-tech-db.github.io/eva/index.html)
* [Slack](https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg)
* [Quick Demo](https://ada-00.cc.gatech.edu/eva/playground)

# EVA Video Database System

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

## QuickStart

1. EVA requires Python 3.7+. To install EVA, we recommend using an virtual environment and the pip package manager:

```shell
pip install evadb
```

1. Start the EVA server and the client programs
```shell
eva_server &   # launch server
eva_client     # launch client
```

2. UPLOAD a video using the client (we use [ua_detrac.mp4](data/ua_detrac/ua_detrac.mp4) video as an example):

```mysql
LOAD FILE "data/ua_detrac/ua_detrac.mp4" INTO MyVideo;
```

3. That's it. You can now start issuing queries over the loaded video:

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

To file a bug or request a feature, please use GitHub issues. Pull requests are welcome.
For more information on installing from source and contributing to EVA, see our
[contributing guidelines](https://evadb.readthedocs.io/en/latest/source/contribute/index.html).

## Contributors

See the [people page](https://github.com/georgia-tech-db/eva/graphs/contributors) for the full listing of contributors.

## License
Copyright (c) 2018-2022 [Georgia Tech Database Group](http://db.cc.gatech.edu/)
Licensed under [Apache License](LICENSE).
