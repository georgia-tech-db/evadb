EVA AI-Relational Database System
====

Over the last decade, deep learning models have radically changed the world of computer vision and natural language processing. They are accurate on a variety of tasks ranging from image classification to question answering. However, there are two challenges that prevent a lot of users from benefiting from these models.

Usability and Application Maintainability
^^^^

To use a vision or language model, the user must do a lot of imperative programming across low-level libraries, like OpenCV, PyTorch, and Hugging Face. This is a tedious process that often leads to a complex program or Jupyter Notebook that glues together these libraries to accomplish the given task. This programming complexity **prevents a lot of people who are experts in other domains from benefiting from these models**.

Historically, database systems have been successful because the **query language is simple enough** in its basic structure that users without prior experience are able to learn a usable subset of the language on their first sitting. EVA supports a declarative SQL-like query language, called EVAQL, that is designed to make it easier for users to leverage these models. With this query language, the user may **compose multiple models in a single query** to accomplish complicated tasks with **minimal programming**. 

Here is a illustrative query that examines the emotions of actors in a movie by leveraging multiple deep learning models that take care of detecting faces and analyzing the emotions of the detected bounding boxes:

.. code:: sql

   SELECT id, bbox, EmotionDetector(Crop(data, bbox)) 
   FROM Interstellar 
        JOIN LATERAL UNNEST(FaceDetector(data)) AS Face(bbox, conf)  
   WHERE id < 15;

By using a declarative language, the complexity of the program or Jupyter Notebook is significantly reduced. This in turn leads to more **maintainable code** that allows users to build on top of each other's queries.

GPU Cost and Human Time 
^^^^

From a cost standpoint, it is very expensive to run these deep learning models on large image or video datasets. For example, the state-of-the-art object detection model takes multiple GPU-decades to process just a year's worth of videos from a single traffic monitoring camera. Besides the money spent on hardware, this also increases the time that the user spends waiting for the model inference process to finish.

EVA **automatically** optimizes the queries to **reduce inference cost and query execution time** using its Cascades-style query optimizer. EVA's optimizer is tailored for video analytics. The `Cascades-style extensible query optimization framework <https://www.cse.iitb.ac.in/infolab/Data/Courses/CS632/Papers/Cascades-graefe.pdf>`_ has worked very well for several decades in SQL database systems. Query optimization is one of the signature components of database systems — `the bridge that connects the declarative query language to efficient execution <http://www.redbook.io/pdf/redbook-5th-edition.pdf>`_.
