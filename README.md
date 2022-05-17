# EVA (Exploratory Video Analytics)

[![Build Status](https://travis-ci.org/georgia-tech-db/eva.svg?branch=master)](https://travis-ci.com/georgia-tech-db/eva)
[![Coverage Status](https://coveralls.io/repos/github/georgia-tech-db/eva/badge.svg?branch=master)](https://coveralls.io/github/georgia-tech-db/eva?branch=master)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Documentation Status](https://readthedocs.org/projects/exvian/badge/?version=latest)](https://evagatech.readthedocs.io/en/latest/index.html) [![Join the chat at https://gitter.im/georgia-tech-db/eva](https://badges.gitter.im/georgia-tech-db/eva.svg)](https://gitter.im/georgia-tech-db/eva?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

## What is EVA?

EVA is a visual data management system (think MySQL for videos). It supports a declarative language similar to SQL and a wide range of commonly used  computer vision models.

## What does EVA do?

* EVA **enables querying of visual data** in user facing applications by providing a simple SQL-like interface for a wide range of commonly used computer vision models.

* EVA **improves throughput** by introducing sampling, filtering, and caching techniques.

* EVA **improves accuracy** by introducing state-of-the-art model specialization and selection algorithms.

## Quick Links
* [EVA website](https://georgia-tech-db.github.io/eva/index.html)
* [EVA tutorials](https://github.com/georgia-tech-db/eva/tree/master/tutorials)
* [EVA documentation](evagatech.readthedocs.io/)
* [EVA community forum](https://gitter.im/georgia-tech-db/eva)

## Installation

### Dependency
EVA requires Python 3.7 or later and JAVA 8. On Ubuntu, you can install the JAVA by `sudo -E apt install -y openjdk-8-jdk openjdk-8-jre`.

### Recommended
To install EVA, we recommend using virtual environment and pip:
```shell
python3 -m venv env37
. env37/bin/activate
pip install --upgrade pip
pip install evatestdb
```

<details><summary>Install from source </summary>
<p>

```bash
git clone https://github.com/georgia-tech-db/eva.git && cd eva
python3 -m venv env37
. env37/bin/activate
pip install --upgrade pip
sh script/antlr4/generate_parser.sh
pip install .
```

</p>
</details>

## QuickStart

1. Set up the server and client
- Activate the virtual environment: `. env37/bin/activate`

- Launch EVA database Server: `eva_server`

- Launch CLI: `eva_client`

2. Run the `UPLOAD` command in the client terminal (use the [ua_detrac.mp4](data/ua_detrac/ua_detrac.mp4) as an example):
```mysql
UPLOAD INFILE 'data/ua_detrac/ua_detrac.mp4' PATH 'test_video.mp4';
```

3. Run the `LOAD` command in the client terminal:
```mysql
LOAD DATA INFILE 'test_video.mp4' INTO MyVideo;
```

4. Below is a basic query that should work on the client
```mysql
SELECT id, data FROM MyVideo WHERE id < 5;
```

## Example Queries
1. Search frames with a pedestrian and a car
```mysql
SELECT id, frame FROM MyVideo WHERE ['pedestrain', 'car'] <@ FastRCNNObjectDetector(frame).labels;
```
2. Search frames containing greater than 3 cars
```mysql
SELECT id, frame FROM DETRAC WHERE array_count(FastRCNNObjectDetector(frame).labels, 'car') > 3;
```

## Documentation

You can find documentation and code snippets for EVA [here](https://evagatech.readthedocs.io/).

## Contributing

To file a bug or request a feature, please file a GitHub issue. Pull requests are welcome.

For information on installing from source and contributing to EVA, see our
[contributing guidelines](./CONTRIBUTING.md).

## Contributors

See the [people page](https://github.com/georgia-tech-db/eva/graphs/contributors) for the full listing of contributors.

## License
Copyright (c) 2018-2022 [Georgia Tech Database Group](http://db.cc.gatech.edu/)
Licensed under the [Apache License](LICENSE).
