Video Database System
====

Over the last decade, deep learning models have radically changed the world of computer vision. They are accurate on a variety of tasks ranging from image classification to emotion detection. However, there are two challenges that prevent a lot of users from benefiting from these models.

Usability and Application Maintainability
^^^^

To use a vision model, the user must do a lot of imperative programming across low-level libraries, like OpenCV and PyTorch. This is a tedious process that often leads to a complex program that glues together these libraries to accomplish the given task. This imperative programming requirement **prevents a lot of people who have expertise in other domains from benefiting from these models**.

Historically, database systems have been successful because the **query language is simple enough** in its basic structure that users without prior experience were able to learn a usable subset on their first sitting. 
EVA supports a declarative SQL-like query language, called EVAQL, that is designed to make it easier for users to leverage these models. With this language, the user may **compose multiple models in a single query** to accomplish complicated tasks with **minimal programming**. 

Here is a illustrative query that examines the emotions of actors in a movie by leveraging multiple deep learning models that take care of detection faces and analyzing the emotions of the detected bounding boxes:

.. code:: sql

   SELECT id, bbox, EmotionDetector(Crop(data, bbox)) 
   FROM Interstellar 
        JOIN LATERAL UNNEST(FaceDetector(data)) AS Face(bbox, conf)  
   WHERE id < 15;

By using a declarative language, the complexity of the program or Jupyter Notebook is significantly reduces. This will lead to more **maintainable code**.

GPU Cost and Human Time 
^^^^

From a cost standpoint, it is often very expensive to run these deep learning models on large image or video datasets. For example, the state-of-the-art object detection model takes multiple GPU-decades to process just a year's worth of videos from a single traffic monitoring camera. This also increases the time that analyst spends waiting for the model inference process to finish. 

EVA **automatically** optimizes the queries to **reduce inference cost and query execution time** using its Cascades-style query optimizer. EVA's optimizer is tailored for video analytics. The `Cascades-style extensible query optimization framework <https://www.cse.iitb.ac.in/infolab/Data/Courses/CS632/Papers/Cascades-graefe.pdf>`_ has worked very well for several decades in SQL database systems. Query optimization is one of the signature components of database systems — `the bridge that connects the declarative query language to efficient execution <http://www.redbook.io/pdf/redbook-5th-edition.pdf>`_.
