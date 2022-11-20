SELECT
======

1. Search frames with a car

.. code:: sql

   SELECT id, frame 
   FROM MyVideo 
   WHERE ['car'] <@ FastRCNNObjectDetector(frame).labels
   ORDER BY id;

2. Search frames with a pedestrian and a car

.. code:: sql

   SELECT id, frame 
   FROM MyVideo 
   WHERE ['pedestrian', 'car'] <@ FastRCNNObjectDetector(frame).labels;

3. Search frames containing greater than 3 cars

.. code:: sql

   SELECT id FROM MyVideo
   WHERE Array_Count(FastRCNNObjectDetector(data).label, 'car') > 3
   ORDER BY id;


4. Compose multiple user-defined functions in a single query

.. code:: sql

   SELECT id, bbox, EmotionDetector(Crop(data, bbox)) 
   FROM HAPPY JOIN LATERAL UNNEST(FaceDetector(data)) AS Face(bbox, conf)  
   WHERE id < 15;

