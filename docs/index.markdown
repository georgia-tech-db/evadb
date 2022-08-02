---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: default
---

# EVA (Exploratory Video Analytics)

[![Build Status](https://travis-ci.org/georgia-tech-db/eva.svg?branch=master)](https://travis-ci.com/georgia-tech-db/eva)
[![Coverage Status](https://coveralls.io/repos/github/georgia-tech-db/eva/badge.svg?branch=master)](https://coveralls.io/github/georgia-tech-db/eva?branch=master)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Documentation Status](https://readthedocs.org/projects/exvian/badge/?version=latest)](https://evagatech.readthedocs.io/en/latest/index.html) 

## What is EVA?

EVA is a video database management system (think MySQL for videos).

* EVA **enables querying of visual data** in user facing applications by providing a simple SQL-like interface for a wide range of commonly used computer vision models.

* EVA **improves throughput** by introducing sampling, filtering, and caching techniques.

* EVA **improves accuracy** by introducing state-of-the-art model specialization and selection algorithms.

![](Img/car.gif)

## Architecture

EVA consists of four core components:

* EVAQL query parser (SQL extended for video analytics)
* Cascades-style query optimizer
* Query execution engine (support for PyTorch and Tensorflow Deep Learning Models, Filter Models)
* Video-centric storage engine

## License
Copyright (c) 2018-2022 [Georgia Tech Database Group](http://db.cc.gatech.edu/)  
Licensed under the [Apache License](https://github.com/georgia-tech-db/eva/blob/website/LICENSE).
