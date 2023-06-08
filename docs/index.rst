.. meta::
   :keywords: database, deep learning, video analytics, language models

EvaDB
=====

..  rubric:: Database system for building simpler and faster AI-powered applications.

..
    ..  figure:: https://raw.githubusercontent.com/georgia-tech-db/eva/master/docs/images/eva/eva-banner.png
        :target: https://github.com/georgia-tech-db/eva
        :width: 100%
        :alt: EvaDB Banner

|pypi_status| |License|

----------

Welcome to EvaDB
=================

EvaDB is an AI-SQL database for developing applications powered by AI models. We aim to simplify the development and deployment of AI-powered applications that operate on structured (tables, feature stores) and unstructured data (videos, text, podcasts, PDFs, etc.).

- Github: https://github.com/georgia-tech-db/eva
- PyPI: https://pypi.org/project/evadb/
- Twitter: https://twitter.com/evadb_ai
- Slack: `Invite link <https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg>`_


Why EvaDB?
----------

Over the last decade, AI models have radically changed the world of natural language processing and computer vision. They are accurate on various tasks ranging from question answering to object tracking in videos. However, two challenges prevent many users from benefiting from these models.

- *Usability*: To use an AI model, the user needs to program against multiple low-level libraries, like OpenCV, PyTorch, and Hugging Face. This tedious process often leads to a complex application that glues together these libraries to accomplish the given task. This programming complexity **prevents people who are experts in other domains from benefiting from these models**.

- *Money and Time*: Running these deep learning models on large video or document datasets is costly and time-consuming. For example, the state-of-the-art object detection model takes multiple GPU years to process just a week's videos from a single traffic monitoring camera. Besides the money spent on hardware, these models also increase the time that you spend waiting for the model inference to finish.

Proposed Solution
----------

That's where EvaDB comes in.

1. Quickly build AI-Powered Applications
^^^^

Historically, SQL database systems have been successful because the **query language is simple enough** in its basic structure that users without prior experience can learn a usable subset of the language on their first sitting. EvaDB supports a simple SQL-like query language designed to make it easier for users to leverage AI models. With this query language, the user may **chain multiple models in a single query** to accomplish complicated tasks with **minimal programming**.

Here is an illustrative query that examines the emotions of actors in a movie by leveraging multiple deep-learning models that take care of detecting faces and analyzing the emotions of the detected bounding boxes:

.. code:: sql

   --- Analyze the emotions of actors in a movie scene
   SELECT id, bbox, EmotionDetector(Crop(data, bbox)) 
   FROM Interstellar 
      JOIN LATERAL UNNEST(FaceDetector(data)) AS Face(bbox, conf)  
   WHERE id < 15;

EvaDB's declarative query language reduces the complexity of the application, leading to **more maintainable code** that allows users to build on top of each other's queries.

EvaDB comes with a wide range of models for analyzing unstructured data including image classification, object detection, OCR, face detection, etc. It is fully implemented in Python, and `licensed under the Apache license <https://github.com/georgia-tech-db/eva>`__. It already contains integrations with widely-used AI pipelines based on Hugging Face, PyTorch, and Open AI. 

The high-level SQL API allows even beginners to use EvaDB in a few lines of code. Advanced users can define custom user-defined functions that wrap around any AI model or Python library.

2. Save time and money
^^^^

EvaDB **automatically** optimizes the queries to **save inference cost and query execution time** using its Cascades-style extensible query optimizer. EvaDB's optimizer is tailored for AI pipelines. The Cascades query optimization framework has worked well in SQL database systems for several decades. Query optimization in EvaDB is the bridge that connects the declarative query language to efficient execution.

EvaDB accelerates AI pipelines using a collection of optimizations inspired by SQL database systems including function caching, sampling, and cost-based operator reordering.

EvaDB supports an AI-oriented query language for analysing both structured and unstructured data. Here are some illustrative applications:

 * `Using ChatGPT to ask questions based on videos <https://evadb.readthedocs.io/en/stable/source/tutorials/08-chatgpt.html>`_
 * `Analysing traffic flow at an intersection <https://evadb.readthedocs.io/en/stable/source/tutorials/02-object-detection.html>`_
 * `Examining the emotion palette of actors in a movie <https://evadb.readthedocs.io/en/stable/source/tutorials/03-emotion-analysis.html>`_
 * `Finding similar images on Reddit <https://evadb.readthedocs.io/en/stable/source/tutorials/11-similarity-search-for-motif-mining.html>`_
 * `Classifying images based on their content <https://evadb.readthedocs.io/en/stable/source/tutorials/01-mnist.html>`_
 * `Image Segmentation using Hugging Face <https://evadb.readthedocs.io/en/stable/source/tutorials/07-object-segmentation-huggingface.html>`_
 * `Recognizing license plates <https://github.com/georgia-tech-db/license-plate-recognition>`_
 * `Analysing toxicity of social media memes <https://github.com/georgia-tech-db/toxicity-classification>`_

The `Getting Started <source/overview/installation.html>`_ page shows how you can use EvaDB for different AI tasks and how you can easily extend EvaDB to support your custom deep learning model through user-defined functions.

The `User Guides <source/tutorials/index.html>`_ section contains Jupyter Notebooks that demonstrate how to use various features of EvaDB. Each notebook includes a link to Google Colab, where you can run the code yourself.

Key Features
------------

1. With EvaDB, you can **easily combine SQL and deep learning models to build next-generation database applications**. EvaDB treats deep learning models as  functions similar to traditional SQL functions like SUM().

2. EvaDB is **extensible by design**. You can write an **user-defined function** (UDF) that wraps around your custom deep learning model. In fact, all the built-in models that are included in EvaDB are written as user-defined functions.

3. EvaDB comes with a collection of **built-in sampling, caching, and filtering optimizations** inspired by relational database systems. These optimizations help **speed up queries on large datasets and save money spent on model inference**.

Next Steps
------------

.. grid:: 1 1 2 2
    :gutter: 3
    :margin: 0
    :padding: 3 4 0 0

    .. grid-item-card:: :doc:`Getting Started <source/overview/installation>`
        :link: source/overview/installation
        :link-type: doc
        
        A step-by-step guide to installing EvaDB and running queries

    .. grid-item-card:: :doc:`Query Language <source/reference/evaql>`
        :link: source/reference/evaql
        :link-type: doc
        
        List of all the query commands supported by EvaDB
    
    .. grid-item-card:: :doc:`User Defined Functions <source/reference/udf>`
        :link: source/reference/udf
        :link-type: doc
        
        A step-by-step tour of registering a user defined function that wraps around a custom deep learning model

----------

Illustrative EvaDB Applications 
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

Join the EvaDB community on `Slack <https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg>`_ to ask questions and to share your ideas for improving EvaDB.

..
    ..  figure:: https://raw.githubusercontent.com/georgia-tech-db/eva/master/docs/images/eva/eva-slack.png
        :target: https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg
        :width: 100%
        :alt: EvaDB Slack Channel

.. |pypi_status| image:: https://img.shields.io/pypi/v/evadb.svg
   :target: https://pypi.org/project/evadb
.. |License| image:: https://img.shields.io/badge/license-Apache%202-brightgreen.svg?logo=apache
   :target: https://github.com/georgia-tech-db/eva/blob/master/LICENSE.txt
