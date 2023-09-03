=========
Concepts
=========

Here is a list of key concepts in EvaDB. If you have any questions, ask the community on `Slack <https://evadb.ai/community>`__.

EvaQL: AI-Centric Query Language
--------------------------------

EvaDB supports a SQL-like query language, called EvaQL, designed to assist software developers in bringing AI into their applications.

Here is set of illustrative EvaQL queries for a ChatGPT-based video question answering app. This EvaDB app connects to collection of news videos stored in a folder and runs an AI query for extracting audio transcripts from the videos using a Hugging Face model, followed by another AI query for question answering using ChatGPT.

.. code-block::sql

    --- Load a collection of news videos into the 'news_videos' table
    --- This command returns a Pandas Dataframe with the query's output
    --- In this case, the output indicates the number of loaded videos
    LOAD VIDEO 'news_videos/*.mp4' INTO VIDEOS;


    --- Define an AI function that wraps around a speech-to-text model 
    --- This model is hosted on Hugging Face which has built-in support in EvaDB
    --- After creating the function, we can use the function in any future query
    CREATE UDF SpeechRecognizer 
        TYPE HuggingFace 
        'task' 'automatic-speech-recognition' 
        'model' 'openai/whisper-base';

    --  EvaDB automatically extracts the audio from the videos
    --- We only need to run the SpeechRecognizer UDF on the 'audio' column 
    --- to get the transcript and persist it in a table called 'transcripts'
    CREATE TABLE transcripts AS 
        SELECT SpeechRecognizer(audio) from news_videos;

    --- Lastly, we run the ChatGPT query for question answering 
    --- This query is based on the 'transcripts' table 
    --- The 'transcripts' table has a column called 'text' with the transcript text
    --- Since ChatGPT is a built-in function in EvaDB, we don't have to define it
    --- We can directly use it in any query
    --- We need to set the OPENAI_KEY as an environment variable
    SELECT ChatGPT('Is this video summary related to Ukraine russia war', text) 
        FROM TEXT_SUMMARY;

EvaQL reduces the complexity of the app, leading to more maintainable code that allows developers to build on top of each other's queries. A single AI query can use multiple AI models to accomplish complicated tasks with minimal programming.

AI-Centric Query Optimization 
-----------------------------

EvaDB optimizes the AI queries to save money spent on running models and reduce query execution time.

EvaDB contains a novel `Cascades-style extensible query optimizer <https://www.cse.iitb.ac.in/infolab/Data/Courses/CS632/Papers/Cascades-graefe.pdf>`__ that is tailored for AI pipelines. Query optimization technology has powered traditional SQL database systems for several decades. Query optimization in EvaDB is the bridge that connects the declarative EvaQL to efficient query execution on CPUs/GPUs.

EvaDB accelerates AI queries using a collection of optimizations inspired by SQL database systems including cost-based function predicate reordering, function caching, sampling, etc.

AI Functions
------------

In EvaDB, functions are typically thin wrappers around AI models. They are extensively used by developers in EvaQL queries.

Here is an illustrative AI function for classifying MNIST images:

.. code-block:: bash

    !wget -nc https://raw.githubusercontent.com/georgia-tech-db/evadb/master/evadb/udfs/mnist_image_classifier.py

.. code-block:: sql

    --- Create an MNIST image classifier function
    --- The function's implementation code is in 'mnist_image_classifier.py'
    CREATE UDF MnistImageClassifier
        IMPL 'mnist_image_classifier.py'

After registering the function, you can use it anywhere in the query -- in the ``select`` or ``filter`` calls.

.. code-block:: sql

    --- Get 'MnistImageClassifier' function's output on frame id 30
    --- This query returns the results of the image classification function
    --- In this case, it is the digit in the 30th frame in the video
    SELECT data, id, MnistImageClassifier(data).label 
    FROM MnistVideo  
    WHERE id = 30;

    --- Use 'MnistImageClassifier' function's output to filter frames
    --- This query returns the frame ids of the frames with digit 6
    --- We limit to the first five frames with digit 6
    SELECT data, id, MnistImageClassifier(data).label 
    FROM MnistVideo  
    WHERE MnistImageClassifier(data).label = '6'
    LIMIT 5;
