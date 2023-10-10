.. _model-inference:

Model Inference
===============

In EvaDB, AI models are simple function calls. 

You can compose SQL queries using AI functions similar to canonical SQL functions like `SUM`. EvaDB automatically optimizes queries with AI functions to save money and time, as detailed in :ref:`optimizations`.

.. note::

   EvaDB ships with a wide range of built-in functions listed in :ref:`models`. If your desired AI model is not available, learn how to easily write your own AI function refer in :ref:`udf`.

1. Projection
-------------

The most common AI queries run models in projection. For example, we can use the `MnistImageClassifier <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/functions/mnist_image_classifier.py>`_ to identify digits.

.. code-block:: sql

   SELECT MnistImageClassifier(data).label FROM mnist_vid;

2. Selection
------------

Another common usecases are model inference in selections. In the below example, we use ``TextSummarizer`` and ``TextClassifier`` from :ref:`HuggingFace<hf>` to summarize the negative food reviews.

.. code-block:: sql

   SELECT TextSummarizer(data)
   FROM food_reviews
   WHERE TextClassifier(data).label = 'NEGATIVE';

EvaDB also provides specialized array operators to construct queries. Go over built-in utility operators and functions for all of them. Below is an example of ``CONTAIN``:

.. code-block:: sql

   SELECT id FROM camera_videos 
   WHERE ObjectDetector(data).labels @> ['person', 'car'];

3. Lateral Join
---------------

In EvaDB, we can also use models in joins.
The most powerful usecase is lateral join combined with ``UNNEST``, which is very helpful to flatten the output from `one-to-many` models.
The key idea here is a model could give multiple outputs (e.g., bounding box) stored in an array. This syntax is used to unroll elements from the array into multiple rows.
Typical examples are `face detectors <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/functions/face_detector.py>`_ and `object detectors <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/functions/fastrcnn_object_detector.py>`_. 
In the below example, we use `emotion detector <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/functions/emotion_detector.py>`_ to detect emotions from faces in the movie, where a single scene can contain multiple faces. 
   
.. code-block:: sql
   
   SELECT EmotionDetector(Crop(data, Face.bbox))
   FROM movie
   LATERAL JOIN UNNEST(FaceDetector(data)) AS Face(bbox, conf);

4. Aggregate Functions
----------------------

Models can also be executed on a sequence of frames, particularly for action detection. This can be accomplished by utilizing ``GROUP BY`` and ``SEGMENT`` to concatenate consecutive frames into a single segment.

.. code-block:: sql

   SELECT ASLActionRecognition(SEGMENT(data)) 
   FROM ASL_ACTIONS 
   SAMPLE 5 
   GROUP BY '16 frames';

Here is another example grouping paragraphs from PDFs:

.. code-block:: sql

   SELECT SEGMENT(data) FROM MyPDFs GROUP BY '10 paragraphs';

5. Order By
-----------
   
Models (typically feature extractors) can also be used in the ``ORDER BY`` for embedding-based similarity search. EvaDB also has index support to facilitate this type of queries.
In the below examples, we use the `SentenceFeatureExtractor <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/functions/sentence_feature_extractor.py>`_ to find relevant context `When was the NATO created` from a collection of pdfs as the knowledge base. Go over `PrivateGPT notebook <https://github.com/georgia-tech-db/evadb/blob/staging/tutorials/13-privategpt.ipynb>`_ for more details.

.. code-block:: sql

   SELECT data FROM MyPDFs
   ORDER BY Similarity(
       SentenceFeatureExtractor('When was the NATO created?'),
       SentenceFeatureExtractor(data)
   );

We can also use the `SiftFeatureExtractor <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/functions/sift_feature_extractor.py>`_ to find similar images from a collection of images as the gallery. Go over :ref:`image-search` for more details.

.. code-block:: sql

   SELECT name FROM reddit_dataset
   ORDER BY Similarity(
       SiftFeatureExtractor(Open('reddit-images/cat.jpg')),
       SiftFeatureExtractor(data)
   );


.. note::

   Go over our :ref:`Usecases<sentiment-analysis>` to check more ways of utilizing models in real-world use cases.
