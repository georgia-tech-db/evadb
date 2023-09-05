:orphan:

Functions
=========

SHOW FUNCTIONS
--------------

Here is a list of built-in user-defined functions in EvaDB.

.. code:: mysql

    SHOW FUNCTIONS;

    id   name                    impl
    0    FastRCNNObjectDetector  evadb/functions/fastrcnn_object_detector.p
    1    MVITActionRecognition   evadb/functions/mvit_action_recognition.py
    2    ArrayCount              evadb/functions/ndarray/array_count.py
    3    Crop                    evadb/evadb/functions/ndarray/crop.py


FastRCNNObjectDetector is a model for detecting objects. MVITActionRecognition is a model for recognizing actions. 

ArrayCount and Crop are utility functions for counting the number of objects in an array and cropping a bounding box from an image, respectively.

SELECT WITH MULTIPLE FUNCTIONS
------------------------------

Here is a query that illustrates how to use multiple functions in a single query.

.. code:: sql

   SELECT id, bbox, EmotionDetector(Crop(data, bbox)) 
   FROM HAPPY JOIN LATERAL UNNEST(FaceDetector(data)) AS Face(bbox, conf)  
   WHERE id < 15;
