=========
Concepts
=========

Here is a list of key concepts in EvaDB. If you have any questions, ask the community on `Slack <https://evadb.ai/community>`__.

EvaQL: AI-Centric Query Language
--------------------------------

EvaDB supports a SQL-like query language, called ``EvaQL``, designed to assist software developers in bringing AI into their applications.

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
        TASK 'automatic-speech-recognition' 
        MODEL 'openai/whisper-base';

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

EvaDB optimizes the AI queries to save money spent on running models and reduce query execution time. It contains a novel `Cascades-style extensible query optimizer <https://www.cse.iitb.ac.in/infolab/Data/Courses/CS632/Papers/Cascades-graefe.pdf>`__  tailored for AI queries. Query optimization has powered traditional SQL database systems for several decades. It is the bridge that connects the declarative query language to efficient query execution on hardware.

EvaDB accelerates AI queries using a collection of optimizations inspired by SQL database systems including cost-based function predicate reordering, function caching, sampling, etc.

AI Functions
------------

``Functions`` are typically thin wrappers around AI models and are extensively used in queries. Here is an `illustrative AI function for classifying MNIST images <https://github.com/georgia-tech-db/evadb/blob/master/evadb/functions/mnist_image_classifier.py>`_. 

To register an user-defined function, use the ``CREATE FUNCTION`` statement:

.. code-block:: sql

    --- Create an MNIST image classifier function
    --- The function's implementation code is in 'mnist_image_classifier.py'
    CREATE FUNCTION MnistImageClassifier
        IMPL 'mnist_image_classifier.py'

After registering ``MnistImageClassifier`` function, you can call the function in the ``SELECT`` and/or ``WHERE`` clauses of any query.

.. code-block:: sql

    --- Get the output of 'MnistImageClassifier' on frame id 30
    --- This query returns the results of the image classification function
    --- In this case, it is the digit in the 30th frame in the video
    SELECT data, id, MnistImageClassifier(data).label 
    FROM MnistVideo  
    WHERE id = 30;

    --- Use the 'MnistImageClassifier' function's output to filter frames
    --- This query returns the frame ids of the frames with digit 6
    --- We limit to the first five frames containing digit 6
    SELECT data, id, MnistImageClassifier(data).label 
    FROM MnistVideo  
    WHERE MnistImageClassifier(data).label = '6'
    LIMIT 5;
