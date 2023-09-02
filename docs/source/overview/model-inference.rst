.. _model-inference:

Model Inference
===============

In EvaDB, every model is a user-defined function. We can compose SQL queries using user-defined functions similar to conventional SQL functions. EvaDB's `cascades optimizer <https://faculty.cc.gatech.edu/~jarulraj/courses/8803-s21/slides/22-cascades.pdf>` will optimize the evaluation of user-defined functions for lower latency. Go over :ref:`optimizations` for more details.

.. note::

   EvaDB ships with a variety of builtin user-defined functions. Go over :ref:`models` to check them. Did not find the desired model? Go over :ref:`custom-udf` to create your own user-defined functions and contribute to EvaDB.

1. Projection

   The most common usecases are model inference in projections. For example, we can use the `MnistImageClassifier <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/udfs/mnist_image_classifier.py>`_ to indefity numbers from the `MINST <https://www.dropbox.com/s/yxljxz6zxoqu54v/mnist.mp4>`_ video. 

.. code-block:: python

   cursor.query("SELECT MnistImageClassifier(data).label FROM minst_vid;").df()

2. Selection

   Another common usecases are model inference in selections. In the below example, we use ``TextSummarizer`` and ``TextClassifier`` from :ref:`HuggingFace<hf-models>` to summarize the negaitve food reviews.

.. code-block:: python

   cursor.query("""
        SELECT TextSummarizer(data) FROM food_reviews
        WHERE TextClassifier(data).label = 'NEGATIVE';
   """).df()

3. Lateral Join

   In EvaDB, we can also use models in joins. The most powerful usecase is lateral join combined with ``UNNEST``, which is very helpful to flatten the output from `one-to-many` models. Typical examples are `face detectors <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/udfs/face_detector.py>`_ and `object detectors <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/udfs/fastrcnn_object_detector.py>`_. In the below example, we use `emotion detector <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/udfs/emotion_detector.py>_` to detect emotions from faces in the movie, where a single scene can contain multiple faces.      

.. code-block:: python

   cursor.query("""
        SELECT EmotionDetector(Crop(data, bbox))
        FROM movie
        LATERAL JOIN UNNEST(FaceDetector(data)) AS Face(bbox, conf);
   """).df()

4. Aggregate Functions

   Models or user-defined functions can also act as aggregate functions for ``GROUP BY``. Typical usecases are action recognition. 

.. code-block:: python

   cursor.query("""
        SELECT ASLActionRecognition(SEGMENT(data)) 
        FROM ASL_ACTIONS 
        SAMPLE 5 
        GROUP BY '16 frames';
   """).df()

5. Order By

   Models (typically feature extractors) can also be used in the ``ORDER BY`` for embedding-based similarity search. EvaDB also has index support to facilitate this type of queries. In the below example, we use the `SentenceFeatureExtractor <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/udfs/sentence_feature_extractor.py>`_ to answer the question `When was the NATO created` from a collection of pdfs as the knowledge base.

.. code-block:: python

   cursor.query("""
        SELECT data FROM MyPDFs
        ORDER BY Similarity(
                SentenceFeatureExtractor('When was the NATO created?'), SentenceFeatureExtractor(data)
        )
   """).df()


.. note::

   Go over our :ref:`Usecases<chatgpt-postgres>` to check variety ways of utlizing models in real-world use cases.
