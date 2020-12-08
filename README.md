# EVA (Exploratory Video Analytics)

[![Build Status](https://travis-ci.org/georgia-tech-db/eva.svg?branch=master)](https://travis-ci.com/georgia-tech-db/eva)
[![Coverage Status](https://coveralls.io/repos/github/georgia-tech-db/eva/badge.svg?branch=master)](https://coveralls.io/github/georgia-tech-db/eva?branch=master)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Documentation Status](https://readthedocs.org/projects/exvian/badge/?version=latest)](https://evagatech.readthedocs.io/en/latest/index.html)

## What is EVA?

EVA is a visual data management system (think MySQL for videos). It supports a declarative language similar to SQL and a wide range of commonly used  computer vision models.

## What does EVA do?

* EVA **enables querying of visual data** in user facing applications by providing a simple SQL-like interface for a wide range of commonly used computer vision models.

* EVA **improves throughput** by introducing sampling, filtering, and caching techniques.

* EVA **improves accuracy** by introducing state-of-the-art model specialization and selection algorithms.

## Table of Contents
* [Installation](#installation)
* [Client Testing](#client-testing)
* [Docker](#docker)
* [Development](#development)
* [Architecture](#architecture)


## Installation

Installation of EVA involves setting a virtual environment using [miniconda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) and configuring git hooks.

1. Clone the repository
```shell
git clone https://github.com/georgia-tech-db/eva.git
```

2. Install the dependencies.
```shell
sh script/install/before_install.sh
export PATH="$HOME/miniconda/bin:$PATH"
sh script/install/install.sh
```

3. Connect mysql user root with normal account and no password
```mysql
sudo mysql -u root
> SELECT User,Host FROM mysql.user;
> DROP USER 'root'@'localhost';
> CREATE USER 'root'@'%' IDENTIFIED BY '';
> GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
> FLUSH PRIVILEGES;
mysql -u root
```
refer to [askubuntu](https://askubuntu.com/questions/766334/cant-login-as-mysql-user-root-from-normal-user-account-in-ubuntu-16-04)

4. Install `docker` and `docker-compose`.
Please refer to [official doc](https://docs.docker.com/engine/install/).

## Client Testing
1. Set up the server and client

- Launch EVA database Server: `python eva.py`

- Launch CLI: `python eva_client.py`

2. Run the `LOAD` command in the client terminal: (may take a while)
```mysql
LOAD DATA INFILE 'data/ua_detrac/ua_detrac.mp4' INTO MyVideo;
```
3. Below is a basic query that should work on the client
```mysql
SELECT id, data FROM MyVideo WHERE id < 5;
```



## Docker

1. Standup EVA testing for CPU/GPU hardware.
```shell
docker-compose -f docker-compose.yml eva-test-[cpu/gpu] up
```

## Development

1. Install git hooks in your .git/ directory. [optional, but recommended]
```shell
conda activate eva
pre-commit install
```

2. Ensure that all the unit test cases (including the ones you have added) run succesfully and the coding style conventions are followed.
```shell
bash script/test/test.sh
```

## Architecture

EVA consists of four core components:

* EVAQL Query Parser
* Query Optimizer
* Query Execution Engine (Filters + Deep Learning Models)
* Distributed Storage Engine

## Contributing

To file a bug or request a feature, please file a GitHub issue. Pull requests are welcome.

## Contributors

See the [people page](https://github.com/georgia-tech-db/eva/graphs/contributors) for the full listing of contributors.

## License
Copyright (c) 2018-2020 [Georgia Tech Database Group](http://db.cc.gatech.edu/)
Licensed under the [Apache License](LICENSE).
