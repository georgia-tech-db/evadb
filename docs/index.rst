.. meta::
   :keywords: database, deep learning, video analytics, language models

Welcome to EvaDB! 
=================

..  rubric:: Database system for building simpler and faster AI-powered apps.

..
    ..  figure:: https://raw.githubusercontent.com/georgia-tech-db/eva/master/docs/images/eva/eva-banner.png
        :target: https://github.com/georgia-tech-db/eva
        :width: 100%
        :alt: EvaDB Banner

|pypi_status| |License|

----------

EvaDB is an AI-SQL database for developing apps powered by AI models. We aim to simplify the development and deployment of AI-powered apps that operate on structured (tables, feature stores) and unstructured data (videos, text, podcasts, PDFs, etc.).

- Github: https://github.com/georgia-tech-db/eva
- PyPI: https://pypi.org/project/evadb/
- Twitter: https://twitter.com/evadb_ai
- Slack: https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg


Why EvaDB?
----------

Over the last decade, AI models have radically changed the world of natural language processing and computer vision. They are accurate on various tasks ranging from question answering to object tracking in videos. However, it is challenging for users to leverage these models due to two challenges:

- *Usability*: To use an AI model, the user needs to program against multiple low-level libraries, like PyTorch, Hugging Face, Open AI, etc. This tedious process often leads to a complex AI app that glues together these libraries to accomplish the given task. This programming complexity prevents people who are experts in other domains from benefiting from these models.

- *Money & Time*: Running these deep learning models on large document or video datasets is costly and time-consuming. For example, the state-of-the-art object detection model takes multiple GPU years to process just a week's videos from a single traffic monitoring camera. Besides the money spent on hardware, these models also increase the time that you spend waiting for the model inference to finish.

Proposed Solution
----------

That is where EvaDB comes in!

1. Quickly build AI-Powered Apps
^^^^

SQL database systems have been successful because the query language is simple enough in its basic structure that users without prior experience can learn a usable subset of the language on their first sitting. EvaDB supports a simple SQL-like query language designed to make it easier for users to leverage AI models. It is easy to chain multiple models in a single query to accomplish complicated tasks with minimal programming.

Here is an illustrative EvaDB app for ChatGPT-based question answering on videos. The app loads a collection of news videos into EvaDB and runs a query for extracting audio transcripts from the videos using a HuggingFace model, followed by question answering using ChatGPT.

.. code:: python

    # pip install evadb and import it
    import evadb

    # Grab a evadb cursor to load data and run queries    
    cursor = evadb.connect().cursor()

    # Load a collection of news videos into the 'news_videos' table
    # This command returns a Pandas Dataframe with the query's output
    # In this case, the output indicates the number of loaded videos
    cursor.load(
        file_regex="news_videos/*.mp4", 
        format="VIDEO", 
        table_name="news_videos"
    ).df()

    # Define a function that wraps around a speech-to-text (Whisper) model 
    # Such functions are known as user-defined functions or UDFs
    # So, we are creating a Whisper UDF here
    # After creating the UDF, we can use the function in any query
    cursor.create_udf(
        udf_name="SpeechRecognizer",
        type="HuggingFace",
        task='automatic-speech-recognition',
        model='openai/whisper-base'
    ).df()

    # EvaDB automatically extract the audio from the video
    # We only need to run the SpeechRecognizer UDF on the 'audio' column 
    # to get the transcript and persist it in a table called 'transcripts'
    cursor.query(
        """CREATE TABLE transcripts AS 
           SELECT SpeechRecognizer(audio) from news_videos;"""
    ).df()

    # We next incrementally construct the ChatGPT query using EvaDB's Python API
    # The query is based on the 'transcripts' table 
    # This table has a column called 'text' with the transcript text
    query = cursor.table('transcripts')

    # Since ChatGPT is a built-in function, we don't have to define it
    # We can just directly use it in the query
    # We need to set the OPENAI_KEY as an environment variable
    os.environ["OPENAI_KEY"] = OPENAI_KEY 
    query = query.select("ChatGPT('Is this video summary related to LLM', text)")

    # Finally, we run the query to get the results as a dataframe
    response = query.df()

.. .. code:: python

..     # Query for analyzing the emotions of actors in a movie scene
..     query = cursor.table("Interstellar")

..     # Run the Face Detection model on the video frames ("data")
..     query = query.cross_apply("UNNEST(FaceDetector(data))", "Face(bbox, conf)")

..     # Add filter based on frame id ("id")
..     query = query.filter("id > 100 AND id < 200")

..     # Crop the bounding box from the frames and 
..     # send the face picture to the Emotion Detection model 
..     query = query.select("id, bbox, EmotionDetector(Crop(data, bbox))")

..     # Get the results as a dataframe
..     # With three columns id, bbox, and emotion
..     response = query.df()

The same AI query can also be written directly in SQL and run on EvaDB.

.. code:: sql

   --- Query for asking question using ChatGPT
   SELECT ChatGPT('Is this video summary related to LLM', 
                  SpeechRecognizer(audio)) FROM news_videos;


EvaDB's declarative query language reduces the complexity of the app, leading to more maintainable code that allows users to build on top of each other's queries.

EvaDB comes with a wide range of models for analyzing unstructured data including image classification, object detection, OCR, face detection, etc. It is fully implemented in Python, and `licensed under the Apache license <https://github.com/georgia-tech-db/eva>`__. It already contains integrations with widely-used AI pipelines based on Hugging Face, PyTorch, and Open AI. 

The high-level SQL API allows even beginners to use EvaDB in a few lines of code. Advanced users can define custom user-defined functions that wrap around any AI model or Python library.

2. Save time and money
^^^^

EvaDB automatically optimizes the queries to save inference cost and query execution time using its Cascades-style extensible query optimizer. EvaDB's optimizer is tailored for AI pipelines. The Cascades query optimization framework has worked well in SQL database systems for several decades. Query optimization in EvaDB is the bridge that connects the declarative query language to efficient execution.

EvaDB accelerates AI pipelines using a collection of optimizations inspired by SQL database systems including function caching, sampling, and cost-based operator reordering.

EvaDB supports an AI-oriented query language for analysing both structured and unstructured data. Here are some illustrative apps:


 * `Reddit Image Similarity Search <https://evadb.readthedocs.io/en/stable/source/tutorials/11-similarity-search-for-motif-mining.html>`_
 * `Using ChatGPT to ask questions based on videos <https://evadb.readthedocs.io/en/stable/source/tutorials/08-chatgpt.html>`_
 * `Querying PDF documents <https://evadb.readthedocs.io/en/stable/source/tutorials/12-query-pdf.html>`_
 * `Analysing traffic flow at an intersection <https://evadb.readthedocs.io/en/stable/source/tutorials/02-object-detection.html>`_
 * `Examining the emotion palette of actors in a movie <https://evadb.readthedocs.io/en/stable/source/tutorials/03-emotion-analysis.html>`_
 * `Classifying images based on their content <https://evadb.readthedocs.io/en/stable/source/tutorials/01-mnist.html>`_
 * `Image Segmentation using Hugging Face <https://evadb.readthedocs.io/en/stable/source/tutorials/07-object-segmentation-huggingface.html>`_
 * `Recognizing license plates <https://github.com/georgia-tech-db/license-plate-recognition>`_
 * `Analysing toxicity of social media memes <https://github.com/georgia-tech-db/toxicity-classification>`_


The `Getting Started <source/overview/installation.html>`_ page shows how you can use EvaDB for different AI tasks and how you can easily extend EvaDB to support your custom deep learning model through user-defined functions.

The `User Guides <source/tutorials/index.html>`_ section contains Jupyter Notebooks that demonstrate how to use various features of EvaDB. Each notebook includes a link to Google Colab, where you can run the code yourself.

Key Features
------------

- 🔮 Build simpler AI-powered apps using short Python or SQL queries
- ⚡️ 10x faster apps using AI-centric query optimization  
- 💰 Save money spent on GPUs
- 🚀 First-class support for your custom deep learning models through user-defined functions
- 📦 Built-in caching to eliminate redundant model invocations across queries
- ⌨️ First-class support for PyTorch, Hugging Face, YOLO, and Open AI models
- 🐍 Installable via pip and fully implemented in Python

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
    
    .. grid-item-card:: :doc:`User Defined Function <source/reference/udfs/custom>`
        :link: source/reference/udfs/custom
        :link-type: doc
        
        A step-by-step tour of registering a user defined function that wraps around a custom deep learning model

----------

Illustrative EvaDB Apps 
----

|:desert_island:| PDF Question Answering
~~~~

..  |pic7| image:: https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/pdf-qa.webp
    :width: 45%
    :alt: App

|pic7|

|:desert_island:| Traffic Analysis App using Object Detection Model
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

|:desert_island:| Movie Analysis App using Face Detection + Emotion Classification Models
~~~~

..  |pic5| image:: https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/gangubai-input.webp
    :width: 45%
    :alt: Source Video

..  |pic6| image:: https://github.com/georgia-tech-db/eva/releases/download/v0.1.0/gangubai-output.webp
    :width: 45%
    :alt: Query Result

|pic5| |pic6|

----------

.. |pypi_status| image:: https://img.shields.io/pypi/v/evadb.svg
   :target: https://pypi.org/project/evadb
.. |License| image:: https://img.shields.io/badge/license-Apache%202-brightgreen.svg?logo=apache
   :target: https://github.com/georgia-tech-db/eva/blob/master/LICENSE.txt
