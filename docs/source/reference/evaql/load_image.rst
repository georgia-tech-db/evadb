LOAD IMAGE
==========

.. _load-image:

.. code:: mysql

   LOAD IMAGE 'test_image.jpg' INTO MyImage;

Images are loaded similarity to videos, each tuple in an image table represents an image. EvaDB automatically generates 
the following schema with two columns: ``name`` and ``data``, that correspond to the image name and the image data.
