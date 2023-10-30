Roadmap
=======

The goal of this doc is to align core and community efforts for the project and to share what's the focus for the next 6 months.

What is the core EvaDB team working on right now?
--------------------------------------------------

Our biggest priorities right now are improving the user experience of LLM data wrangling and classical AI tasks (e.g., regression, classification, and forecasting).

LLM data wrangling
~~~~~~~~~~~~~~~~~~

* Prompt Engineering: more flexibility of constructing prompt and better experience/feedback to tune the prompt. 
* LLM Cache: reuse the LLM calls based on the model, prompt, and input columns.
* LLM Batch: intelligently group multiple LLM calls into one to reduce the cost and latency. 
* Cost Calculation and Estimation: show the cost (i.e., time, token usage, and dollars) of the query at the plan time and after execution.

Classical AI tasks
~~~~~~~~~~~~~~~~~~

* Accuracy: show the accuracy of the training.
* Configuration guidance: provide guidance and suggestion on how to configure the AutoML framework (e.g., which frequency to use for forcasting).
* Cost calculation and estimation: show the cost (i.e., time) of the query the plan time and after exectuion.
* Path to Scale: improve the processing pipeline for large datasets.

What areas are great for community contributions?
--------------------------------------------------

.. note::
   If you are unsure about your idea, feel free to chat with us in the **#community** channel in our `Slack <https://evadb.ai/slack>`_.

We are looking forward to expand our integrations including data sources and AI functions, where we can use them with the rest of the ecosystem of EvaDB. 

Example Data Sources
~~~~~~~~~~~~~~~~~~~~

`GitHub <https://github.com/georgia-tech-db/evadb/tree/staging/evadb/third_party/databases/github>`_ is one application data sources we have added in EvaDB. These application data sources help the user to develop AI applications without the needs of extracting, loading, and transforming data. Example application data sources that are not in EvaDB yet, but we think can boost the AI applications, include (but not limited to) the following:

* YouTube
* Google Search
* Reddit
* arXiv 

When adding a data source to EvaDB, we do expect a documentation page to explain the usage. This is an `example documentation page <https://evadb.readthedocs.io/en/stable/source/reference/databases/github.html>`_ for the GitHub integration.

Example AI functions
~~~~~~~~~~~~~~~~~~~~

Adding more AI functions in EvaDB can give users more choices and possibilities for developing AI applications.
`Stable Diffusion <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/functions/stable_diffusion.py>`_ is an example AI function in EvaDB that generates an image given a prompt.
Example AI functions that are not in EvaDB yet, but we think can boost the AI applications, include (but not limited to) the following:

* Sklearn (besides the linear regression)
* OCR (PyTesseract)
* AWS Rekognition service  
 
When adding a AI function to EvaDB, we do expect a documentation page to explain the usage. This is an `example documetation page <https://evadb.readthedocs.io/en/latest/source/reference/ai/stablediffusion.html>`_ for Stable Diffusion. Optionally, but highly recommended is also to have a notebook to showcase the use cases.
Example `notebook <https://colab.research.google.com/github/georgia-tech-db/eva/blob/master/tutorials/18-stable-diffusion.ipynb>`_ for Stable Diffusion.

