.. _stablediffusion:

Stable Diffusion Models
======================================

This section provides an overview of how you can generate images from prompts in EvaDB using a Stable Diffusion model.


Introduction
------------

Stable Diffusion models leverage a controlled random walk process to generate intricate patterns and images from textual prompts,
bridging the gap between text and visual representation. EvaDB uses the stable diffusion implementation from `Replicate <https://replicate.com>`_.

Stable Diffusion UDF
--------------------

In order to create an image generation function in EvaDB, use the following SQL command:

.. code-block:: sql

    CREATE FUNCTION IF NOT EXISTS StableDiffusion
    IMPL 'evadb/functions/stable_diffusion.py';

EvaDB automatically uses the latest `stable diffusion release <https://replicate.com/stability-ai/stable-diffusion/versions>`_ available on Replicate.

To see a demo of how the function can be used, please check the `demo notebook <https://colab.research.google.com/github/georgia-tech-db/eva/blob/master/tutorials/18-stable-diffusion.ipynb>`_ on stable diffusion.