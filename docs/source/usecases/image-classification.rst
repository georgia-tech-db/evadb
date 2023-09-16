.. _image-classification:

Image Classification
====================

.. raw:: html

    <embed>
    <table align="left">
    <td>
        <a target="_blank" href="https://colab.research.google.com/github/georgia-tech-db/eva/blob/staging/tutorials/01-mnist.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run on Google Colab</a>
    </td>
    <td>
        <a target="_blank" href="https://github.com/georgia-tech-db/eva/blob/staging/tutorials/01-mnist.ipynb"><img src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a>
    </td>
    <td>
        <a target="_blank" href="https://github.com/georgia-tech-db/eva/raw/staging/tutorials/01-mnist.ipynb"><img src="https://www.tensorflow.org/images/download_logo_32px.png" /> Download notebook</a>
    </td>
    </table><br><br>
    </embed>

Introduction
------------

In this tutorial, we present how to use ``PyTorch`` models in EvaDB to classify images. In particular, we focus on classifying images from the ``MNIST`` dataset that contains ``digits``. EvaDB makes it easy to do image classification using its built-in support for ``PyTorch`` models.

In this tutorial, besides classifying images, we will also showcase a query where the model's output is used to retrieve images with the digit ``6``.

.. include:: ../shared/evadb.rst

We will assume that the input ``MNIST`` video is loaded into ``EvaDB``. To download the video and load it into ``EvaDB``, see the complete `image classification notebook on Colab <https://colab.research.google.com/github/georgia-tech-db/eva/blob/master/tutorials/01-mnist.ipynb>`_.

Create Image Classification Function
------------------------------------

To create a custom ``MnistImageClassifier`` function, use the ``CREATE FUNCTION`` statement. The code for the custom classification model is available `here <https://github.com/georgia-tech-db/evadb/blob/master/evadb/functions/mnist_image_classifier.py>`_.

We will assume that the file is downloaded and stored as ``mnist_image_classifier.py``. Now, run the following query to register the AI function:

.. code-block:: sql

        CREATE FUNCTION 
        IF NOT EXISTS MnistImageClassifier 
        IMPL 'mnist_image_classifier.py';

Image Classification Queries
----------------------------

After the function is registered in ``EvaDB``, you can use it subsequent SQL queries in different ways. 

In the following query, we call the classifier on every image in the video. The output of the function is stored in the ``label`` column (i.e., the digit associated with the given frame) of the output ``DataFrame``.

.. code-block:: sql

    SELECT MnistImageClassifier(data).label 
    FROM mnist_video;

This query returns the label of all the images:

.. code-block:: 

    +------------------------------+
    |   mnistimageclassifier.label |
    |------------------------------|
    |                            6 |
    |                            6 |
    |                          ... |
    |                          ... |
    |                          ... |
    |                          ... |
    |                            4 |
    |                            4 |
    +------------------------------+


Filtering Based on AI Function
------------------------------

In the following query, we use the output of the classifier to retrieve a subset of images that contain a particular digit (e.g., ``6``).

.. code-block:: sql

    SELECT id, MnistImageClassifier(data).label 
        FROM mnist_video 
        WHERE MnistImageClassifier(data).label = '6';

Now, the ``DataFrame`` only contains images of the digit ``6``.

.. code-block:: 

    +------------------------------+
    |   mnistimageclassifier.label |
    |------------------------------|
    |                            6 |
    |                            6 |
    +------------------------------+

.. include:: ../shared/footer.rst