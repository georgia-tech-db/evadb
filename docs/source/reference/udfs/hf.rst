HuggingFace Models
======================

This section provides an overview of how you can use out-of-the-box HuggingFace models in EVA.


Creating UDF from HuggingFace
------------------------------

EVA supports UDFS similar to `Pipelines <https://huggingface.co/docs/transformers/main_classes/pipelines>`_  in HuggingFace. 

.. code-block:: sql

    CREATE UDF IF NOT EXISTS HFObjectDetector
    TYPE  HuggingFace
    'task' 'object-detection'
    'model' 'facebook / detr-resnet-50'

EVA supports all arguments supported by HF pipelines. You can pass those using a key value format similar to task and model above.

To pass arguments to the inference function, you can use the `INFERENCE_` prefix in the argument name. 

.. code-block:: sql

    CREATE UDF IF NOT EXISTS HFObjectDetector
    TYPE  HuggingFace
    'task' 'automatic-speech-recognition' 
    'model' 'openai/whisper-base'
    'INFERENCE_return_timestamps' 'True';

This would be similar to passing `return_timestamps=True` to HF pipeline during inference.

Supported Tasks
-----
EVA supports the following tasks from huggingface:

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
- Named Entity Recognition