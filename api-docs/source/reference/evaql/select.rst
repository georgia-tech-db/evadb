SELECT query
==============

Illustrative queries:

1. Search frames with a car

.. code:: sql

   SELECT id, frame FROM MyVideo WHERE ['car'] <@ FastRCNNObjectDetector(frame).labels;

2. Search frames with a pedestrian and a car

.. code:: sql

   SELECT id, frame FROM MyVideo WHERE ['pedestrian', 'car'] <@ FastRCNNObjectDetector(frame).labels;

.. code:: sql

   SELECT id, frame FROM MyVideo WHERE array_count(FastRCNNObjectDetector(frame).labels, 'car') > 3;

3. Search frames containing greater than 3 cars

.. code:: sql

   SELECT id, frame FROM DETRAC WHERE array_count(FastRCNNObjectDetector(frame).labels, 'car') > 3;
