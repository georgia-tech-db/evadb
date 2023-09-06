Ultralytics Models
=========================

This section provides an overview of how you can use out-of-the-box Ultralytics models in EvaDB.


Creating YOLO Model
-------------------

To create a YOLO function in EvaDB using Ultralytics models, use the following SQL command:

.. code-block:: sql

    CREATE FUNCTION IF NOT EXISTS Yolo
    TYPE ultralytics
    MODEL 'yolov8m.pt'

You can change the `model` value to specify any other model supported by Ultralytics.

Supported Models
----------------

The following models are currently supported by Ultralytics in EvaDB:

- yolov8n.pt
- yolov8s.pt
- yolov8m.pt
- yolov8l.pt
- yolov8x.pt

Please refer to the `Ultralytics documentation <https://docs.ultralytics.com/tasks/detect/#models>`_ for more information about these models and their capabilities.

Using Ultralytics Models with Other Functions
---------------------------------------------
This code block demonstrates how the YOLO model can be combined with other models such as Color and DogBreedClassifier to perform more specific and targeted object detection tasks. In this case, the goal is to find images of black-colored Great Danes.

The first query uses YOLO to detect all images of dogs with black color. The ``UNNEST`` function is used to split the output of the ``Yolo`` function into individual rows, one for each object detected in the image. The ``Color`` function is then applied to the cropped portion of the image to identify the color of each detected dog object. The ``WHERE`` clause filters the results to only include objects labeled as "dog" and with a color of "black".

.. code-block:: sql

    SELECT id, bbox FROM dogs 
    JOIN LATERAL UNNEST(Yolo(data)) AS Obj(label, bbox, score) 
    WHERE Obj.label = 'dog' 
    AND Color(Crop(data, bbox)) = 'black'; 


The second query builds upon the first by further filtering the results to only include images of Great Danes. The ``DogBreedClassifier`` function is used to classify the cropped portion of the image as a Great Dane. The ``WHERE`` clause adds an additional condition to filter the results to only include objects labeled as "dog", with a color of "black", and classified as a "great dane".

.. code-block:: sql

    SELECT id, bbox FROM dogs 
    JOIN LATERAL UNNEST(Yolo(data)) AS Obj(label, bbox, score) 
    WHERE Obj.label = 'dog' 
    AND DogBreedClassifier(Crop(data, bbox)) = 'great dane' 
    AND Color(Crop(data, bbox)) = 'black';