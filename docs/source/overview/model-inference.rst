.. _model-inference:

Model Inference
===============

In EvaDB, every model is a function. We can compose SQL queries using functions as building units similar to conventional SQL functions. EvaDB's `cascades optimizer <https://faculty.cc.gatech.edu/~jarulraj/courses/8803-s21/slides/22-cascades.pdf>`_ will optimize the evaluation of user-defined functions for lower latency. Go over :ref:`optimizations` for more details.

.. note::

   EvaDB ships with a variety of builtin user-defined functions. Go over :ref:`models` to check them. Did not find the desired model? Go over :ref:`udf` to create your own user-defined functions and contribute to EvaDB.

1. Projection
-------------

The most common usecases are model inference in projections. For example, we can use the `MnistImageClassifier <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/functions/mnist_image_classifier.py>`_ to identify numbers from the `MINST <https://www.dropbox.com/s/yxljxz6zxoqu54v/mnist.mp4>`_ video. 

.. code-block:: sql

   SELECT MnistImageClassifier(data).label FROM minst_vid;

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
In the below example, we use `emotion detector <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/functions/emotion_detector.py>_` to detect emotions from faces in the movie, where a single scene can contain multiple faces. 
   
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

   Go over our :ref:`Usecases<sentiment-analysis>` to check more ways of utlizing models in real-world use cases.
