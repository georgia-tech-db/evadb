=========
Concepts
=========

These are some high-level concepts related to EvaDB. If you still have questions after reading this documents,  ping us on `our Slack <https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg>`__!


Quickly build AI-Powered Apps
---------------------------------

EvaDB supports a simple SQL-like query language designed to make it easier for users to leverage AI models. It is easy to chain multiple models in a single query to accomplish complicated tasks with minimal programming.

Here is an illustrative EvaDB app for ChatGPT-based question answering on videos. The app loads a collection of news videos into EvaDB and runs a query for extracting audio transcripts from the videos using a HuggingFace model, followed by question answering using ChatGPT.

.. code-block:: python
    
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
    # After creating the function, we can use the function in any future query
    cursor.create_function(
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


The same AI query can also be written directly in SQL and run on EvaDB.

.. code-block:: sql

    --- Query for asking question using ChatGPT
    SELECT ChatGPT('Is this video summary related to LLM', 
                SpeechRecognizer(audio)) FROM news_videos;

EvaDB's declarative query language reduces the complexity of the app, leading to more maintainable code that allows users to build on top of each other's queries.

EvaDB comes with a wide range of models for analyzing unstructured data including image classification, object detection, OCR, face detection, etc. It is fully implemented in Python, and `licensed under the Apache license <https://github.com/georgia-tech-db/evadb>`__. It already contains integrations with widely-used AI pipelines based on Hugging Face, PyTorch, and Open AI.

The high-level SQL API allows even beginners to use EvaDB in a few lines of code. Advanced users can define custom user-defined functions that wrap around any AI model or Python library.

Save time and money
----------------------

EvaDB automatically optimizes the queries to save inference cost and query execution time using its Cascades-style extensible query optimizer. EvaDB's optimizer is tailored for AI pipelines. The Cascades query optimization framework has worked well in SQL database systems for several decades. Query optimization in EvaDB is the bridge that connects the declarative query language to efficient execution.

EvaDB accelerates AI pipelines using a collection of optimizations inspired by SQL database systems including function caching, sampling, and cost-based operator reordering.

EvaDB supports an AI-oriented query language for analyzing both structured and unstructured data. Here are some illustrative apps:


The `Getting Started <source/overview/installation.html>`__ page shows how you can use EvaDB for different AI tasks and how you can easily extend EvaDB to support your custom deep learning model through user-defined functions.

The `User Guides <source/tutorials/index.html>`__ section contains Jupyter Notebooks that demonstrate how to use various features of EvaDB. Each notebook includes a link to Google Colab, where you can run the code yourself.




User-Defined Function (UDF) or Function
------------------------------------------

User-defined functions are thin wrappers around deep learning models. They 
allow us to use deep learning models in AI queries.

Here is an illustrative UDF for classifying MNIST images.

.. code-block:: bash

    !wget -nc https://raw.githubusercontent.com/georgia-tech-db/evadb/master/evadb/udfs/mnist_image_classifier.py

.. code-block:: python

    cursor.create_function("MnistImageClassifier", True, 'mnist_image_classifier.py')
    response = cursor.df()
    print(response)

That's it! You can now use the newly registered UDF anywhere in the query -- in the ``select`` or ``filter`` calls.

.. code-block:: python

    query = cursor.table("MNISTVideo")
    query = query.filter("id = 30 OR id = 50 OR id = 70")

    # Here, we are selecting the output of the function
    query = query.select("data, MnistImageClassifier(data).label")
    response = query.df()

.. code-block:: python

    query2 = cursor.table("MNISTVideo")

    # Here, we are also filtering based on the output of the function
    query2 = query2.filter("MnistImageClassifier(data).label = '6' AND id < 10")
    query2 = query2.select("data, MnistImageClassifier(data).label")
    response = query2.df()