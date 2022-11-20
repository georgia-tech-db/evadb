Exploratory Video Analytics
=====

..  figure:: https://raw.githubusercontent.com/georgia-tech-db/eva/master/docs/assets/img/eva-banner.png
    :target: https://github.com/georgia-tech-db/eva
    :width: 100%
    :alt: EVA Banner

|pypi_status| |License| |Discuss| |Python Versions|

What is EVA?
------------

`EVA <https://github.com/georgia-tech-db/eva>`_ is a new database system tailored for video analytics -- think PostgreSQL for videos. It supports a SQL-like language for querying videos (e.g., finding frames in a movie with an actor or finding touchdowns in a football game). It comes with a wide range of commonly used computer vision models.

Key Features
------------

1. With EVA, you can **easily combine SQL and deep learning models to build next-generation database applications**. EVA treats deep learning models as  functions similar to traditional SQL functions like SUM().

2. EVA is **extensible by design**. You can write an **user-defined function** (UDF) that wraps arounds your custom deep learning model. In fact, all the built-in models that are included in EVA are written as user-defined functions.

3. EVA comes with a collection of **built-in sampling, caching, and filtering optimizations** inspired by relational database systems. These optimizations help **speed up queries on large datasets and save money spent on model inference**.

Next Steps
------------

.. grid:: 1 1 2 2
    :gutter: 3
    :margin: 0
    :padding: 3 4 0 0

    .. grid-item-card:: :doc:`Getting Started <source/overview/installation>`
        :link: source/overview/installation
        :link-type: doc
        
        A step-by-step guide to installing EVA and running queries

    .. grid-item-card:: :doc:`Query Language <source/reference/evaql>`
        :link: source/reference/evaql
        :link-type: doc
        
        List of all the query commands supported by EVA
    
    .. grid-item-card:: :doc:`User Defined Functions <source/reference/udf>`
        :link: source/reference/udf
        :link-type: doc
        
        A step-by-step tour of registering a user defined function that wraps around a custom deep learning model

Illustrative EVA Applications 
----

|:desert_island:| Traffic Analysis Application using Object Detection Model
~~~~

.. |pic1| image:: https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/traffic-input.webp
    :width: 45%
    :alt: Source Video

.. |pic2| image:: https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/traffic-output.webp
    :width: 45%
    :alt: Query Result

|pic1| |pic2|

|:desert_island:| MNIST Digit Recognition using Image Classification Model
~~~~

..  |pic3| image:: https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/mnist-input.webp
    :width: 20%
    :alt: Source Video

..  |pic4| image:: https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/mnist-output.webp
    :width: 20%
    :alt: Query Result

|pic3| |pic4|

|:desert_island:| Movie Analysis Application using Face Detection + Emotion Classfication Models
~~~~

..  |pic5| image:: https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/gangubai-input.webp
    :width: 45%
    :alt: Source Video

..  |pic6| image:: https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/gangubai-output.webp
    :width: 45%
    :alt: Query Result

|pic5| |pic6|

Community
----

Join the EVA community on `Slack <https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg>`_ to ask questions and to share your ideas for improving EVA.

..  figure:: https://raw.githubusercontent.com/georgia-tech-db/eva/master/docs/assets/img/eva-slack.jpg
    :target: https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg
    :width: 100%
    :alt: EVA Slack Channel

.. spelling::

.. |pypi_status| image:: https://img.shields.io/pypi/v/evadb.svg
   :target: https://pypi.org/project/evadb
.. |License| image:: https://img.shields.io/badge/license-Apache%202-brightgreen.svg?logo=apache
   :target: https://github.com/georgia-tech-db/eva/blob/master/LICENSE.txt
.. |Discuss| image:: https://img.shields.io/badge/-Discuss!-blueviolet
   :target: https://github.com/georgia-tech-db/eva/discussions
.. |Python Versions| image:: https://img.shields.io/badge/Python--versions-3.7+-brightgreen
   :target: https://github.com/georgia-tech-db/eva

