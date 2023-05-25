Why EVA?
====

Over the last decade, deep learning models have radically changed the world of computer vision and natural language processing. They are accurate on a variety of tasks ranging from image classification to question answering. However, there are two challenges that prevent a lot of users from benefiting from these models.

1. Easy-to-build AI-Powered Applications
^^^^

To use a vision or language model, the user needs to program against multiple low-level libraries, like OpenCV, PyTorch, and Hugging Face. This is a tedious process that often leads to a complex Python program or Jupyter Notebook that glues together these libraries to accomplish the given task. This programming complexity **prevents a lot of people who are experts in other domains from benefiting from these models**.

Historically, database systems have been successful because the **query language is simple enough** in its basic structure that users without prior experience are able to learn a usable subset of the language on their first sitting. EVA supports a declarative SQL-like query language, called EVA-QL, that is designed to make it easier for users to leverage these models. With this query language, the user may **compose multiple models in a single query** to accomplish complicated tasks with **minimal programming**. 

Here is a illustrative query that examines the emotions of actors in a movie by leveraging multiple deep learning models that take care of detecting faces and analyzing the emotions of the detected bounding boxes:

.. code:: sql

   --- Analyze emotions of actors in a movie scene
   SELECT id, bbox, EmotionDetector(Crop(data, bbox)) 
   FROM Interstellar 
      JOIN LATERAL UNNEST(FaceDetector(data)) AS Face(bbox, conf)  
   WHERE id < 15;

By using a declarative language, the complexity of the application is significantly reduced. This in turn leads to more **maintainable code** that allows users to build on top of each other's queries.

2. Save time and money!
^^^^

It is very expensive to run these deep learning models on large video or document datasets. For example, the state-of-the-art object detection model takes multiple GPU-years to process just a week's worth of videos from a single traffic monitoring camera. Besides the money spent on hardware, this also increases the time that you spend waiting for the model inference to finish.

EVA **automatically** optimizes the queries to **reduce inference cost and query execution time** using its Cascades-style query optimizer. EVA's optimizer is tailored for AI pipelines. The Cascades query optimization framework has worked very well for several decades in SQL database systems.Query optimization in EVA is the bridge that connects the declarative query language to efficient execution.