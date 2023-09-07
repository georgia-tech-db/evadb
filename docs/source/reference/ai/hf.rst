.. _hf:

HuggingFace Models
======================

This section provides an overview of how you can use out-of-the-box HuggingFace models in EvaDB.


Creating Function from HuggingFace
----------------------------------

EvaDB supports functions similar to `Pipelines <https://huggingface.co/docs/transformers/main_classes/pipelines>`_  in HuggingFace. 

.. code-block:: sql

    CREATE FUNCTION IF NOT EXISTS HFObjectDetector
    TYPE  HuggingFace
    TASK 'object-detection'
    MODEL 'facebook / detr-resnet-50'

EvaDB supports all arguments supported by HF pipelines. You can pass those using a key value format similar to task and model above.

Supported Tasks
----------------
EvaDB supports the following tasks from huggingface:

- Audio Classification
- Automatic Speech Recognition
- Text Classification
- Summarization
- Text2Text Generation
- Text Generation
- Image Classification
- Image Segmentation
- Image-to-Text
- Object Detection
- Depth Estimation
