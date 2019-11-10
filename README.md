# EVA (Exploratory Video Analytics)

[![Build Status](https://travis-ci.org/georgia-tech-db/Eva.svg?branch=master)](https://travis-ci.com/georgia-tech-db/Eva)
[![Coverage Status](https://coveralls.io/repos/github/georgia-tech-db/Eva/badge.svg?branch=master)](https://coveralls.io/github/georgia-tech-db/Eva?branch=master)

EVA is an end-to-end video analytics engine that allows users to query a database of videos and return results based on machine learning analysis. 

## Table of Contents
* [Installation](#installation)
* [Demos](#demos)
* [Unit Tests](#unit-tests)
* [Eva Core](#eva-core)
* [Eva Storage](#eva-storage)
* [Dataset](#dataset) 


## Installation
Installation of EVA involves setting a virtual environment using conda and configuring git hooks.

1. Clone the repo
```shell
git clone https://github.com/georgia-tech-db/Eva.git
```

2. Install [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/) and update path.
```shell
export PATH=~/anaconda3/bin:$PATH
```

3. Install dependencies in a virtual environment. Dependencies should install with no errors on Ubuntu 16.04 but there are known installation issues with MacOS.
```shell
cd Eva/
conda env create -f environment.yml
```

4. Run following command to configure git hooks.
```shell
git config core.hooksPath .githooks
```
    
## Demos
The following components have demos:

1. EVA Analytics: A pipeline for loading a dataset, training filters, and outputting the optimal plan.
```commandline
   cd <YOUR_EVA_DIRECTORY>
   source activate eva_35
   python pipeline.py
```
2. EVA Query Optimizer: The optimizer shows converted queries
 (Will show converted queries for the original queries)
```commandline
   cd <YOUR_EVA_DIRECTORY>
   source activate eva_35
   python query_optimizer/query_optimizer.py
```
3. Eva Loader (Loads UA-DETRAC dataset)
```commandline
   cd <YOUR_EVA_DIRECTORY>
   source activate eva_35
   python loaders/load.py
```

4. NEW!!! There are new versions of the loaders and filters.
```commandline
   cd <YOUR_EVA_DIRECTORY>
   source activate eva_35
   python loaders/uadetrac_loader.py
   python filters/minimum_filter.py
```

5. EVA storage-system (Video compression and indexing system - *currently in progress*)

## Unit Tests
To run unit tests on the system, the following commands can be run:

```shell
   pycodestyle --select E test src/loaders
   pytest test/ --cov-report= --cov=./ -s -v
``` 

## Eva Core
Eva core is consisted of
* Query Optimizer
* Filters
* UDFs
* Loaders

#### Query Optimizer
The query optimizer converts a given query to the optimal form. 

All code related to this module is in */query_optimizer*

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

All code related to this module is in */filters*

#### UDFs
This module contains all imported deep learning models. Currently, there is no code that performs this task. It is a work in progress.
Information of current work is explained in detail [here](src/udfs/README.md).

All related code should be inside */udfs*

#### Loaders
The loaders load the dataset with the attributes specified in the *Accelerating Machine Learning Inference with Probabilistic Predicates* by Yao et al.

All code related to this module is in */loaders*

## Eva Storage
Currently a work in progress. Come check back later!


## Dataset
__[Dataset info](data/README.md)__ explains detailed information about the  datasets




