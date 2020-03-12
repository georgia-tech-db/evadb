# EVA (Exploratory Video Analytics)

[![Build Status](https://travis-ci.org/georgia-tech-db/eva.svg?branch=master)](https://travis-ci.com/georgia-tech-db/eva)
[![Coverage Status](https://coveralls.io/repos/github/georgia-tech-db/eva/badge.svg?branch=master)](https://coveralls.io/github/georgia-tech-db/eva?branch=master)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## What is EVA?

EVA is a visual data management system (think MySQL for videos). It supports a declarative language similar to SQL and a wide range of commonly used  computer vision models.

## What does EVA do?

* EVA **enables querying of visual data** in user facing applications by providing a simple SQL-like interface for a wide range of commonly used computer vision models. 

* EVA **improves throughput** by introducing sampling, filtering, and caching techniques.

* EVA **improves accuracy** by introducing state-of-the-art model specialization and selection algorithms.

## Table of Contents
* [Installation](#installation)
* [Development](#development)
* [Architecture](#architecture)

## Installation

Installation of EVA involves setting a virtual environment using [miniconda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) and configuring git hooks.

1. Clone the repository
```shell
git clone https://github.com/georgia-tech-db/eva.git
```

2. Install [miniconda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) and update the `PATH` environment variable.
```shell
export PATH="$HOME/miniconda/bin:$PATH" 
```

3. Install dependencies in a miniconda virtual environment. Virtual environments keep dependencies in separate sandboxes so you can switch between both `eva` and other Python applications easily and get them running.
```shell
cd eva/
conda env create -f environment.yml
```

Run the following command to update an existing environment after updating the `environment.yml` file:
```shell
conda env update --name eva --file environment.yml
```

4. Activate the `eva` environment.
```shell
conda activate eva
```

5. Run the following command to configure the git hooks.
```shell
git config core.hooksPath .githooks
```
6. Run following command to generate parser files.
```shell
sh ./script/antlr4/setup.sh
```

## Development

1. Ensure that all the unit test cases (including the ones you have added) run succesfully.

```shell
   python -m pytest --cov-report= --cov=src/ -s --log-level=INFO 
```

To run the unit tests in a particular file (e.g., `test_parser.py`:

```shell
   python -m pytest --cov-report= --cov=src/ -s --log-level=INFO test/parser/test_parser.py
```

2. Ensure that the coding style conventions are followed.

```shell
   pycodestyle  --select E src/ test/ --exclude src/filters,src/parser/evaql
``` 

3. Run the formatter script to automatically fix most of the coding style issues.

```shell
   python script/formatting/formatter.py
```

4. Follow the [Google Python style guide](https://google.github.io/styleguide/pyguide.html).

## Architecture 

EVA consists of four core components:

* Query Parser
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
