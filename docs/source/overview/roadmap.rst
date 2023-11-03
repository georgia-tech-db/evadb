Roadmap
=======

The goal of this roadmap is to align the efforts of the core EvaDB team and community contributors by describing the biggest focus areas for the next 6 months:

.. note::
   Please ping us on our `Slack <https://evadb.ai/slack>`_ if you any questions or feedback on these focus areas. 

LLM-based Data Wrangling
------------------------

* Prompt Engineering: more flexibility of constructing prompt and better developer experience/feedback to tune the prompt.
* LLM Cache: Reuse the results of LLM calls based on the model, prompt, and input columns.
* LLM Batching: Intelligently group multiple LLM calls into a single call to reduce cost and latency.
* LLM Cost Calculation and Estimation: Show the estimated cost metrics (i.e., time, token usage, and dollars) of the query at optimization time and the actual cost metrics after query execution.

Classical AI Tasks
------------------


* Accuracy: Show the accuracy of the training loop.
* Configuration Guidance: Provide guidance on how to configure the AutoML framework (e.g., which frequency to use for forecasting).
* Task Cost calculation and Estimation: Show the estimated cost metrics (i.e., time) of the query at optimization time and the actual cost metrics after execution.
* Path to Scalability: Improve the efficiency of the query processing pipeline for large datasets.

More Application Data Sources
-----------------------------


`GitHub <https://github.com/georgia-tech-db/evadb/tree/staging/evadb/third_party/databases/github>`_ is an application data source already available in EvaDB. Such data sources allow the developer to quickly build AI applications without focusing on extracting, loading, and transforming data from the application. 

Data sources that are not available in EvaDB yet, but would be super relevant for emerging AI applications, include (but not limited to) the following applications:

* YouTube
* Google Search
* Reddit
* arXiv 
* Hacker News

When adding a data source to EvaDB, please add a documentation page in your PR  explaining the usage. Here is the `illustrative documentation page <https://evadb.readthedocs.io/en/stable/source/reference/databases/github.html>`_ for the GitHub data source in EvaDB.

More AI functions
-----------------

Adding more AI functions in EvaDB will accelerate AI app development using EvaDB. `Stable Diffusion <https://github.com/georgia-tech-db/evadb/blob/staging/evadb/functions/stable_diffusion.py>`_ is an illustrative AI function in EvaDB that generates an image given a text prompt.

AI functions that are not available in EvaDB yet, but would be super relevant for emerging AI applications, include (but not limited to) the following:

* Sklearn (beyond linear regression)
* OCR (PyTesseract)
* AWS Rekognition service
 
When adding an AI function to EvaDB, please add a documentation page in your PR explaining the usage. Here is the `documentation page <https://evadb.readthedocs.io/en/latest/source/reference/ai/stablediffusion.html>`_ for Stable Diffusion.

Notebooks are also super helpful to showcase use-cases! Here is an illustrative `notebook <https://colab.research.google.com/github/georgia-tech-db/eva/blob/master/tutorials/18-stable-diffusion.ipynb>`_ on using Stable Diffusion in EvaDB queries.
