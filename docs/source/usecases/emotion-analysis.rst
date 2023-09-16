.. _emotion-analysis:

Emotion Analysis
================

.. raw:: html

    <embed>
    <table align="left">
    <td>
        <a target="_blank" href="https://colab.research.google.com/github/georgia-tech-db/eva/blob/staging/tutorials/03-emotion-analysis.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run on Google Colab</a>
    </td>
    <td>
        <a target="_blank" href="https://github.com/georgia-tech-db/eva/blob/staging/tutorials/03-emotion-analysis.ipynb"><img src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a>
    </td>
    <td>
        <a target="_blank" href="https://github.com/georgia-tech-db/eva/raw/staging/tutorials/03-emotion-analysis.ipynb"><img src="https://www.tensorflow.org/images/download_logo_32px.png" /> Download notebook</a>
    </td>
    </table><br><br>
    </embed>

Introduction
------------

In this tutorial, we present how to use ``PyTorch`` models in EvaDB to detect faces and classify their emotions. In particular, we focus on detecting faces in a person's video and classifying their emotions. EvaDB makes it easy to do face detection and emotion classification using its built-in support for ``PyTorch`` models.

In this tutorial, we will showcase an usecase where we ``chain`` the outputs of two AI models in a single query. After detecting faces, we will ``crop`` the bounding box of the detected face and send it to an ``EmotionDetector`` function.

.. include:: ../shared/evadb.rst

We will assume that the input ``defhappy`` video is loaded into ``EvaDB``. To download the video and load it into ``EvaDB``, see the complete `emotion analysis notebook on Colab <https://colab.research.google.com/github/georgia-tech-db/eva/blob/master/tutorials/03-emotion-analysis.ipynb>`_.

Create Face and Emotion Detection Functions
-------------------------------------------

To create custom ``FaceDetector`` and ``EmotionDetector`` functions, use the ``CREATE FUNCTION`` statement. In these queries, we leverage EvaDB's built-in support for custom models. We will assume that the files containing these functions are downloaded and stored locally. Now, run the following queries to register these functions:

.. code-block:: sql

        CREATE UDF IF NOT EXISTS FaceDetector
            INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
            OUTPUT (bboxes NDARRAY FLOAT32(ANYDIM, 4),
                    scores NDARRAY FLOAT32(ANYDIM))
            TYPE  FaceDetection
            IMPL  'face_detector.py';

        CREATE FUNCTION IF NOT EXISTS EmotionDetector 
            INPUT (frame NDARRAY UINT8(3, ANYDIM, ANYDIM)) 
            OUTPUT (labels NDARRAY STR(ANYDIM), 
                    scores NDARRAY FLOAT32(ANYDIM)) 
            TYPE  Classification 
            IMPL 'emotion_detector.py';

The ``FaceDetector`` function takes a ``frame`` as input (``NDARRAY`` type) and returns bounding boxes (``bboxes``) of detected faces along with corresponding confidence scores (``scores``).

The ``EmotionDetector`` function takes a ``frame`` as input (``NDARRAY`` type) and returns a label along with the corresponding confidence score.

Emotion Analysis Queries
------------------------

After the functions are registered in ``EvaDB``, you can use them in subsequent SQL queries in different ways. 

In the following query, we call the ``FaceDetector`` function on every image in the video. The output of the function is stored in the ``bboxes`` and ``scores`` columns of the output ``DataFrame``.

.. code-block:: sql

    SELECT id, FaceDetector(data) 
    FROM HAPPY
    WHERE id < 10;

This query returns the faces detected in the first ten frames of the video:

.. code-block:: 

    +----------+---------------------+-------------------------+
    | happy.id | facedetector.bboxes |   facedetector.scores   |
    +----------+---------------------+-------------------------+
    |    0     | [[499  94 761 435]  |  [0.9999081 0.791269 ]  |
    |          |  [237 296 326 399]] |                         |
    |    1     | [[501  95 763 436]  |  [0.9999021 0.8090978]  |
    |          |  [238 296 325 399]] |                         |
    |    2     | [[503  96 767 439]] |       [0.9998859]       |
    |    3     | [[499  90 776 447]] |      [0.99995923]       |
    |    4     | [[498 100 768 444]] |      [0.99999774]       |
    |    5     | [[504  89 778 439]  |  [0.9999716 0.8267602]  |
    |          |  [236 305 324 406]] |                         |
    |    6     | [[500  88 779 451]] |       [0.9999136]       |
    |    7     | [[502  88 780 450]] |      [0.99990165]       |
    |    8     | [[504  90 783 450]  | [0.9999368  0.72843623] |
    |          |  [235 308 325 411]] |                         |
    |    9     | [[508  90 785 448]  | [0.99992466 0.7014416 ] |
    |          |  [235 309 325 412]] |                         |
    +----------+---------------------+-------------------------+

Chaining Functions in a Single AI Query 
---------------------------------------

In the following query, we use the output of the ``FaceDetector`` to crop the detected face from the frame and send it to the ``EmotionDetector`` to identify the emotion in that person's face. Here, ``Crop`` is a built-in function in EvaDB that is used for cropping the given bounding box (``bbox``) from the given frame (``data``). 

We use ``LATERAL JOIN`` clause in the query to map the output of the ``FaceDetector`` to each frame in the ``HAPPY`` video table.

.. code-block:: sql

    SELECT id, bbox, EmotionDetector(Crop(data, bbox)) 
    FROM HAPPY 
         JOIN LATERAL UNNEST(FaceDetector(data)) AS Face(bbox, conf)  
    WHERE id < 15;

Now, the ``DataFrame`` only contains the emotions of the detected faces:

.. code-block:: 

    +----------+-------------------+------------------------+------------------------+
    | happy.id |     Face.bbox     | emotiondetector.labels | emotiondetector.scores |
    +----------+-------------------+------------------------+------------------------+
    |    0     | [499  94 761 435] |         happy          |   0.9996277093887329   |
    |    0     | [237 296 326 399] |        neutral         |   0.8095587491989136   |
    |    1     | [501  95 763 436] |         happy          |   0.9996333122253418   |
    |    1     | [238 296 325 399] |        neutral         |   0.5969993472099304   |
    |    2     | [503  96 767 439] |         happy          |   0.999674916267395    |
    |    3     | [499  90 776 447] |         happy          |   0.9996751546859741   |
    |    4     | [498 100 768 444] |         happy          |   0.9996353387832642   |
    |    5     | [504  89 778 439] |         happy          |   0.9996645450592041   |
    |    5     | [236 305 324 406] |        neutral         |   0.7656209468841553   |
    |    6     | [500  88 779 451] |         happy          |   0.999667763710022    |
    |    7     | [502  88 780 450] |         happy          |   0.9996945858001709   |
    |    8     | [504  90 783 450] |         happy          |   0.9996901750564575   |
    |    8     | [235 308 325 411] |        neutral         |   0.6952931880950928   |
    |    9     | [508  90 785 448] |         happy          |   0.9996936321258545   |
    |    9     | [235 309 325 412] |        neutral         |   0.6790497899055481   |
    |    10    | [508  89 788 449] |         happy          |   0.9997019171714783   |
    |    10    | [235 311 323 413] |        neutral         |   0.7205461263656616   |
    |    11    | [514  87 789 454] |         happy          |   0.9997119307518005   |
    |    12    | [513  87 789 454] |         happy          |   0.9997120499610901   |
    |    13    | [513  87 789 456] |         happy          |   0.9997060894966125   |
    |    14    | [515  88 790 454] |         happy          |   0.9997135996818542   |
    +----------+-------------------+------------------------+------------------------+

.. include:: ../shared/footer.rst
