.. _ai-queries:

AI Queries
==========

In EvaDB, AI models are simple function calls similar to traditional SQL functions like ``MAX``. 

This page details how you can use AI models in different ways to construct AI queries in EvaDB. EvaDB automatically optimizes AI queries to save money and time, as detailed in the :ref:`optimizations<optimizations>` page.

.. note::

   EvaDB ships with a wide range of built-in functions listed in the :ref:`models` page. If your desired AI model is not available, you can also bring your own AI function by referring to the :ref:`custom_ai_function` page.

SELECT Clause
-------------

AI queries often contain the AI function(s) in the ``SELECT`` clause (projection list).

For example, the following query calls the `MnistImageClassifier <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/functions/mnist_image_classifier.py>`_ function to identify digits in a collection of frames in the `mnist_video`.

.. code-block:: sql

   SELECT MnistImageClassifier(data).label FROM mnist_video;

WHERE Clause
------------

Another common position in the AI query with model inference is the ``WHERE`` clause (selection). 

For example, the following query uses the ``TextSummarizer`` and ``TextClassifier`` functions from the :ref:`HuggingFace<hf>` AI engine to summarize the sentiment of food reviews and identify those expressing a `negative` sentiment in the ``SELECT`` and ``WHERE`` clauses, respectively.

.. code-block:: sql

   SELECT TextSummarizer(data)
   FROM food_reviews
   WHERE TextClassifier(data).label = 'NEGATIVE';


ARRAY Operators
---------------

EvaDB supports specialized array operators. 

For example, the following query applies the ``CONTAIN`` operator (``@>``) on the output of an object detection function:

.. code-block:: sql

   SELECT id 
   FROM camera_videos 
   WHERE ObjectDetector(data).labels @> ['person', 'car'];


Here is another query with the ``UNNEST`` function that flattens the output of an `one-input-to-many-outputs` AI function.

.. code-block:: sql

   SELECT UNNEST(FaceDetector(data)) AS Face(bbox, conf)
   FROM movie;

The `face detector <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/functions/face_detector.py>`_ model returns multiple outputs (e.g., bounding box and confidence score) as an array. The ``UNNEST`` function unrolls elements from the array into multiple rows.

LATERAL JOIN
------------

For more challenging AI apps, EvaDB supports lateral joins.

The following AI query uses both a ``LATERAL JOIN`` and an ``UNNEST`` function to detect emotions from faces in a movie, where a single scene may contain multiple faces. The output of the `object detector <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/functions/fastrcnn_object_detector.py>`_ is used to crop the bounding box from the image, and the cropped image is then sent to an `emotion detector <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/functions/emotion_detector.py>`_ to detect the emotion of the face inside the bounding box.
   
.. code-block:: sql
   
   SELECT EmotionDetector(Crop(data, Face.bbox))
   FROM movie
   LATERAL JOIN UNNEST(FaceDetector(data)) AS Face(bbox, conf);

Ordering 
--------

AI models may also be used in the ``ORDER BY`` clause to enable usecases like similarity search.

For example, in the following query, the output of the `SentenceFeatureExtractor <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/functions/sentence_feature_extractor.py>`_ 
is used to find relevant context for answering the user's question (`When was the NATO created`) from a collection of PDFs.

.. code-block:: sql

   SELECT data FROM MyPDFs
   ORDER BY Similarity(
       SentenceFeatureExtractor('When was the NATO created?'),
       SentenceFeatureExtractor(data)
   );

Similarity search maps to ordering based on the distance computed by the `Similarity` function, between the features extracted from the query and those extracted from the paragraphs loaded from the documents. EvaDB automatically accelerates such queries using vector databases.

.. note::
   Go over the `PrivateGPT <https://github.com/georgia-tech-db/evadb/blob/staging/tutorials/13-privategpt.ipynb>`_ notebook for more details.

Given a queried image, we can use a different feature extractor (`SiftFeatureExtractor <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/functions/sift_feature_extractor.py>`_ function) to find the most similar image from an existing collection of images (`reddit_dataset`).

.. code-block:: sql

   SELECT name 
   FROM reddit_dataset
   ORDER BY Similarity(
       SiftFeatureExtractor(Open('reddit-images/cat.jpg')),
       SiftFeatureExtractor(data)
   );

.. note::
   Go over the :ref:`Image Search <image-search>` page for more details.


Aggregate Functions
-------------------

AI models can be applied on a sequence of tuples using the ``GROUP BY`` and ``SEGMENT`` clauses. 

The following query concatenates consecutive frames in a movie into a single segment and applies an action recognition model on the segment:

.. code-block:: sql

   SELECT ASLActionRecognition(SEGMENT(data)) 
   FROM ASL_ACTIONS 
   SAMPLE 5 
   GROUP BY '16 frames';

Here is another illustrative query that groups together paragraphs from a PDF document:

.. code-block:: sql

   SELECT SEGMENT(data) 
   FROM MyPDFs 
   GROUP BY '10 paragraphs';


.. note::

   The :ref:`use cases <sentiment-analysis>` illustrate more ways of utilizing AI queries for building AI apps.
