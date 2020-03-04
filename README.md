# EVA (Exploratory Video Analytics)

[![Build Status](https://travis-ci.org/georgia-tech-db/eva.svg?branch=master)](https://travis-ci.com/georgia-tech-db/eva)
[![Coverage Status](https://coveralls.io/repos/github/georgia-tech-db/eva/badge.svg?branch=master)](https://coveralls.io/github/georgia-tech-db/eva?branch=master)

EVA is an end-to-end video analytics engine that allows users to query a database of videos and return results based on machine learning analysis. 

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

4. Activate the `eva` environment.
```shell
conda activate eva
```

5. Run following command to configure git hooks.
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

4. Refer [google codestyle guide](https://google.github.io/styleguide/pyguide.html) for documentation of code.

Please look up the [contributing guide](https://github.com/georgia-tech-db/eva/blob/master/CONTRIBUTING.md#development) for details.

## Architecture 

The EVA visual data management system consists of four core components:

* Query Parser
* Query Optimizer
* Query Execution Engine (Filters + UDFs)
* Storage Engine (Loaders)

#### Query Optimizer
The query optimizer converts a given query to the optimal form. 

Module location: *src/query_optimizer*

#### Filters
The filters does preliminary filtering to video frames using cheap machine learning models.
The filters module also outputs statistics such as reduction rate and cost that is used by Query Optimizer module.

The preprocessing method below is running:
* PCA

The filters below are running:
* KDE
* DNN
* Random Forest
* SVM

Module location: *src/filters*

#### UDFs
This module contains all imported deep learning models. Currently, there is no code that performs this task. It is a work in progress.
Information of current work is explained in detail [here](src/udfs/README.md).

Module location: *src/udfs*

#### Loaders
The loaders load the dataset with the attributes specified in the *Accelerating Machine Learning Inference with Probabilistic Predicates* by Yao et al.

Module location: *src/loaders*

## Status

_Technology preview_: currently unsupported, possibly due to incomplete functionality or unsuitability for production use.

## Contributors

See the [people page](https://github.com/georgia-tech-db/eva/graphs/contributors) for the full listing of contributors.

## License
Copyright (c) 2018-2020 [Georgia Tech Database Group](http://db.cc.gatech.edu/)  
Licensed under the [Apache License](LICENSE).
