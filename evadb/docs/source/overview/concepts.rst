=========
Concepts
=========

EvaDB is designed around three key concepts: 

(1) AI Queries
(2) AI Functions
(3) AI-Centric Query Optimization

.. note::

    Have a question or want to give feedback? Join us on `Slack <https://evadb.ai/community>`__!

AI Queries
----------

EvaDB supports a high-level, declarative language for writing AI queries that is similar to SQL. Software developers can bring AI-powered features into their database applications using AI queries. 

Here are some illustrative **AI queries** for a ChatGPT-based video question answering app. This AI app first connects to collection of news videos stored in a local folder. It then runs an AI query for extracting audio transcripts from the videos using a Hugging Face model. Lastly, it runs another AI query for answering the user's question over the transcript using ChatGPT.

.. code-block:: sql

    --- Load a collection of news videos into the 'news_videos' table
    --- This command returns a Pandas Dataframe with the query's output
    --- In this case, the output indicates the number of loaded videos
    LOAD VIDEO 'news_videos/*.mp4' INTO VIDEOS;


    --- Define an AI function that wraps around a speech-to-text model 
    --- This model is hosted on Hugging Face which has built-in support in EvaDB
    --- After creating the function, we can use the function in any future query
    CREATE FUNCTION SpeechRecognizer 
        TYPE HuggingFace 
        TASK 'automatic-speech-recognition' 
        MODEL 'openai/whisper-base';

    --  EvaDB automatically extracts the audio from the videos
    --- We only need to run the SpeechRecognizer function on the 'audio' column 
    --- to get the transcript and persist it in a table called 'transcripts'
    CREATE TABLE transcripts AS 
        SELECT SpeechRecognizer(audio) from news_videos;

    --- Lastly, we run the ChatGPT query for question answering 
    --- This query is based on the 'transcripts' table 
    --- The 'transcripts' table has a column called 'text' with the transcript text
    --- Since ChatGPT is a built-in function in EvaDB, we don't have to define it
    --- We can directly use ChatGPT() in any query
    --- We will only need to set the OPENAI_API_KEY as an environment variable
    SELECT ChatGPT('Is this video summary related to Ukraine russia war', text) 
        FROM TEXT_SUMMARY;

By reducing the complexity of the AI app to a few short, simple queries, EvaDB helps in writing **more maintainable, extensible, and scalable** AI apps. 

You can build on top of AI queries written by other developers. You can **chain together** multiple AI models in a single query to accomplish complicated tasks with minimal programming.

AI Functions
------------

In EvaDB, ``functions`` are typically thin wrappers around AI models and are extensively used in AI queries.

Here is an `illustrative AI function for classifying the digit in MNIST images <https://github.com/georgia-tech-db/evadb/blob/master/evadb/functions/mnist_image_classifier.py>`_. 

To register an user-defined function, we use the :ref:`CREATE FUNCTION<create-function>` statement:

.. code-block:: sql

    --- Create an MNIST image classifier function
    --- The function's implementation is in the 'mnist_image_classifier.py' file
    CREATE FUNCTION MnistImageClassifier
        IMPL 'mnist_image_classifier.py'

After registering ``MnistImageClassifier`` function, you can call the function in the ``SELECT`` and/or ``WHERE`` clauses of any query.

.. code-block:: sql

    --- Get the output of 'MnistImageClassifier' on the 30th video frame (id=30)
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

AI-Centric Query Optimization
-----------------------------

EvaDB optimizes the AI queries to save money spent on running models and reduce query execution time. It contains a novel `Cascades-style query optimizer <https://faculty.cc.gatech.edu/~jarulraj/courses/8803-s21/slides/22-cascades.pdf>`__  tailored for AI queries.

Query optimization has powered SQL database systems for several decades. It is the bridge that connects the declarative query language to efficient query execution on hardware. EvaDB accelerates AI queries using a collection of optimizations detailed in the :ref:`optimizations<optimizations>` page.
