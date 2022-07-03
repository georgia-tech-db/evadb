# EVA (Exploratory Video Analytics)

[![Build Status](https://circleci.com/gh/georgia-tech-db/eva.svg?style=svg)](https://circleci.com/gh/georgia-tech-db/eva)
[![Coverage Status](https://coveralls.io/repos/github/georgia-tech-db/eva/badge.svg?branch=master)](https://coveralls.io/github/georgia-tech-db/eva?branch=master)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Documentation Status](https://readthedocs.org/projects/exvian/badge/?version=latest)](https://evagatech.readthedocs.io/en/latest/index.html) [![Join the chat at https://gitter.im/georgia-tech-db/eva](https://badges.gitter.im/georgia-tech-db/eva.svg)](https://gitter.im/georgia-tech-db/eva?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

## What is EVA?

EVA is a visual data management system (think MySQL for videos). It supports a declarative language similar to SQL and a wide range of commonly used  computer vision models.

## What does EVA do?

* EVA **enables querying of visual data** in user facing applications by providing a simple SQL-like interface for a wide range of commonly used computer vision models.

* EVA **improves throughput** by introducing sampling, filtering, and caching techniques.

* EVA **improves accuracy** by introducing state-of-the-art model specialization and selection algorithms.

## Links
* [Demo](https://ada-00.cc.gatech.edu/eva/playground)
* [Website](https://georgia-tech-db.github.io/eva/index.html)
* [Documentation](https://evagatech.readthedocs.io/en/latest/)
* [Tutorials](https://github.com/georgia-tech-db/eva/tree/master/tutorials)
* [Chat](https://gitter.im/georgia-tech-db/eva)

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

2. UPLOAD a video using the client terminal (we use [ua_detrac.mp4](data/ua_detrac/ua_detrac.mp4) video as an example):

```mysql
UPLOAD INFILE 'data/ua_detrac/ua_detrac.mp4' PATH 'test_video.mp4';
```

3. LOAD the video using the client terminal:

```mysql
LOAD DATA INFILE 'test_video.mp4' INTO MyVideo;
```

4. That's it. You can now start issuing queries over that video:

```mysql
SELECT id, data FROM MyVideo WHERE id < 5;
```

## More Interesting Queries

1. Search for frames in a video that contain a car

```mysql
SELECT id, data FROM MyVideo WHERE ['car'] <@ FastRCNNObjectDetector(data).labels;
```
![QueryResult](https://georgia-tech-db.github.io/eva/Img/car.gif)

2. Search for frames in a video that contain  a pedestrian and a car

```mysql
SELECT id, data FROM MyVideo WHERE ['pedestrian', 'car'] <@ FastRCNNObjectDetector(data).labels;
```
## Extending new DDL command in EVA
Now EVA support following DDL commands:
* CREATE
* RENAME
* DROP
* TRUNCATE

For the tutorial of implementing a DDL command, please refer to  `tutorial_extend_ddl_cmd.md`.

3. Search frames in a video containing more than 3 cars

```mysql
SELECT id, data FROM MyVideo WHERE Array_Count(FastRCNNObjectDetector(data).labels, 'car') > 3;
```

4. Materialize the objects detected in a video

```mysql
CREATE MATERIALIZED VIEW IF NOT EXISTS MyVideoObjects (id, labels, scores, bboxes) AS 
SELECT id, FastRCNNObjectDetector(data) FROM MyVideo;
```

5. Create a metadata table that keeps tracks of details about objects in a video

```mysql
CREATE TABLE IF NOT EXISTS MyCSV (
                id INTEGER UNIQUE,
                frame_id INTEGER,
                video_id INTEGER,
                dataset_name TEXT(30),
                label TEXT(30),
                bbox NDARRAY FLOAT32(4),
                object_id INTEGER
);
UPLOAD INFILE 'data/ua_detrac/metadata.csv' PATH 'test_metadata.csv';
LOAD DATA INFILE 'test_metadata.csv' INTO MyCSV WITH FORMAT CSV;
```

## Documentation

Documentation for EVA is located [here](https://evagatech.readthedocs.io/).

### Installation Instructions for Developers

To install EVA from source, use a virtual environment and the pip package manager. EVA requires JAVA 8 for generating the parser.

```shell
git clone https://github.com/georgia-tech-db/eva.git && cd eva
python3 -m venv env38                                # to create a virtual environment
. env38/bin/activate
pip install --upgrade pip
sudo -E apt install -y openjdk-8-jdk openjdk-8-jre   # to install JAVA
sh script/antlr4/generate_parser.sh                  # to generate the EVA parser
pip install .
```

</p>
</details>


## Contributing

To file a bug or request a feature, please use GitHub issues. Pull requests are welcome.

For information on installing from source and contributing to EVA, see our
[contributing guidelines](./CONTRIBUTING.md).

## Contributors

See the [people page](https://github.com/georgia-tech-db/eva/graphs/contributors) for the full listing of contributors.

## License
Copyright (c) 2018-2022 [Georgia Tech Database Group](http://db.cc.gatech.edu/)
Licensed under [Apache License](LICENSE).
