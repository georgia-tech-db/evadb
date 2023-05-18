.. meta::
   :keywords: database, deep learning, video analytics, language models

EVA DB
=====

..  rubric:: Database system for building simpler and faster AI-powered applications.

..  figure:: https://raw.githubusercontent.com/georgia-tech-db/eva/master/docs/images/eva/eva-banner.png
    :target: https://github.com/georgia-tech-db/eva
    :width: 100%
    :alt: EVA Banner

|pypi_status| |License|

----------

What is EVA?
------------

EVA is an **open-source AI-relational database with first-class support for deep learning models**. It aims to support AI-powered database applications that operate on both structured (tables) and unstructured data (videos, text, podcasts, PDFs, etc.) with deep learning models.

EVA accelerates AI pipelines using a collection of optimizations inspired by relational database systems including function caching, sampling, and cost-based operator reordering. It comes with a wide range of models for analyzing unstructured data including image classification, object detection, OCR, face detection, etc. It is fully implemented in Python, and `licensed under the Apache license <https://github.com/georgia-tech-db/eva>`__.

EVA supports a AI-oriented query language for analysing unstructured data. Here are some illustrative applications:

 * `Using ChatGPT to ask questions based on videos <https://evadb.readthedocs.io/en/stable/source/tutorials/08-chatgpt.html>`_
 * `Analysing traffic flow at an intersection <https://evadb.readthedocs.io/en/stable/source/tutorials/02-object-detection.html>`_
 * `Examining the emotion palette of actors in a movie <https://evadb.readthedocs.io/en/stable/source/tutorials/03-emotion-analysis.html>`_
 * `Finding similar images on Reddit <https://evadb.readthedocs.io/en/stable/source/tutorials/11-similarity-search-for-motif-mining.html>`_
 * `Classifying images based on their content <https://evadb.readthedocs.io/en/stable/source/tutorials/01-mnist.html>`_
 * `Image Segmentation using Hugging Face <https://evadb.readthedocs.io/en/stable/source/tutorials/07-object-segmentation-huggingface.html>`_
 * `Recognizing license plates <https://github.com/georgia-tech-db/license-plate-recognition>`_
 * `Analysing toxicity of social media memes <https://github.com/georgia-tech-db/toxicity-classification>`_


If you are wondering why you might need a AI-Relational database system, start with page on `AI-Relational Database Systems <source/overview/aidb.html>`_. It describes how EVA lets users easily make use of deep learning models and how they can reduce money spent on inference on large image or video datasets.

The `Getting Started <source/overview/installation.html>`_ page shows how you can use EVA for different computer vision tasks, and how you can easily extend EVA to support your custom deep learning model in the form of user-defined functions.

The `User Guides <source/tutorials/index.html>`_ section contains Jupyter Notebooks that demonstrate how to use various features of EVA. Each notebook includes a link to Google Colab, where you can run the code by yourself.

Key Features
------------

1. With EVA, you can **easily combine SQL and deep learning models to build next-generation database applications**. EVA treats deep learning models as  functions similar to traditional SQL functions like SUM().

2. EVA is **extensible by design**. You can write an **user-defined function** (UDF) that wraps around your custom deep learning model. In fact, all the built-in models that are included in EVA are written as user-defined functions.

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

----------

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

|:desert_island:| Movie Analysis Application using Face Detection + Emotion Classification Models
~~~~

..  |pic5| image:: https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/gangubai-input.webp
    :width: 45%
    :alt: Source Video

..  |pic6| image:: https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/gangubai-output.webp
    :width: 45%
    :alt: Query Result

|pic5| |pic6|

----------

Community
--------

Join the EVA community on `Slack <https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg>`_ to ask questions and to share your ideas for improving EVA.

..  figure:: https://raw.githubusercontent.com/georgia-tech-db/eva/master/docs/images/eva/eva-slack.png
    :target: https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg
    :width: 100%
    :alt: EVA Slack Channel

.. |pypi_status| image:: https://img.shields.io/pypi/v/evadb.svg
   :target: https://pypi.org/project/evadb
.. |License| image:: https://img.shields.io/badge/license-Apache%202-brightgreen.svg?logo=apache
   :target: https://github.com/georgia-tech-db/eva/blob/master/LICENSE.txt
