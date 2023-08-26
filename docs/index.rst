.. meta::
   :keywords: database, deep learning, video analytics, language models

Welcome to EvaDB! 
=================

..  rubric:: Database system for building simpler and faster AI-powered apps.

..
    ..  figure:: https://raw.githubusercontent.com/georgia-tech-db/evadb/master/docs/images/evadb/evadb-banner.png
        :target: https://github.com/georgia-tech-db/evadb
        :width: 100%
        :alt: EvaDB Banner

.. |pypi_status| image:: https://img.shields.io/pypi/v/evadb.svg
   :target: https://pypi.org/project/evadb
.. |License| image:: https://img.shields.io/badge/license-Apache%202-brightgreen.svg?logo=apache
   :target: https://github.com/georgia-tech-db/evadb/blob/master/LICENSE.txt


|pypi_status| |License|

----------

EvaDB is an open-source unified framework for developing AI-powered apps on top of your data sources. It offers a SQL-like declarative language to simplify the development and deployment of AI-powered apps, which can work with structured data (such as tables and feature stores) and unstructured data (like videos, text, podcasts, PDFs, and more).

- Github: https://github.com/georgia-tech-db/evadb
- PyPI: https://pypi.org/project/evadb/
- Twitter: https://twitter.com/evadb_ai
- Slack: https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg


Why EvaDB?
----------

Over the last decade, AI models have radically changed the world of natural language processing and computer vision. They are accurate on various tasks ranging from question answering to object tracking in videos. However, it is challenging for users to leverage these models due to two challenges:

- **Usability**: To use an AI model, the user needs to program against multiple low-level libraries, like PyTorch, Hugging Face, Open AI, etc. This tedious process often leads to a complex AI app that glues together these libraries to accomplish the given task. This programming complexity prevents people who are experts in other domains from benefiting from these models.

- **Money & Time**: Running these deep learning models on large document or video datasets is costly and time-consuming. For example, the state-of-the-art object detection model takes multiple GPU years to process just a week's videos from a single traffic monitoring camera. Besides the money spent on hardware, these models also increase the time that you spend waiting for the model inference to finish.

Getting Started
----------------

.. raw:: html

    <div class="grid-container">
    <a class="no-underline" href="source/overview/getting-started.html" target="_blank"> <div class="info-box" >
            <div class="image-header" style="padding:0px;">
                <img src="_static/icons/code.png" width="44px" height="44px" />
                <h3 style="font-size:20px;">Learn basics</h3>
            </div>
            <p class="only-light" style="color:#000000;">Understand how to use EvaDB to build AI apps.</p> 
            <p class="only-dark" style="color:#FFFFFF;">Understand how to use EvaDB to build AI apps.</p>    
            <p style="font-weight:600;">Learn more > </p>  
    </div> </a>  
    <a class="no-underline" href="source/overview/concepts.html" target="_blank"> 
        <div class="info-box" >
            <div class="image-header" style="padding:0px;">
                <img src="_static/icons/download.png" width="44px" height="44px" />
                <h3 style="font-size:20px;">Features</h3>
            </div>
            <p class="only-light" style="color:#000000;">Learn about the EvaDB features.</p> 
            <p class="only-dark" style="color:#FFFFFF;">Learn about the EvaDB features.</p>      
            <p style="font-weight:600;">Learn more > </p>  
        </div> 
    </a>  
    <a class="no-underline" href="https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg"  target="_blank" 
            ><div class="info-box" >
            <div class="image-header" style="padding:0px;">
                <img src="_static/icons/slack.png" width="44px" height="44px" />
                <h3 style="font-size:20px;">Join Slack</h3>
            </div>
            <p class="only-light" style="color:#000000;">Have a question? Join our Slack community.</p> 
            <p class="only-dark" style="color:#FFFFFF;">Have a question? Join our Slack community.</p>   
            <p style="color:#515151;"></p>
            <p style="font-weight:600;">Support > </p> 
    </div></a>
    </div>


Key Features
------------

- 🔮 Build simpler AI-powered apps using short Python functions or SQL queries
- ⚡️ 10x faster AI apps using AI-centric query optimization  
- 💰 Save money spent on GPUs
- 🚀 First-class support for your custom deep learning models through user-defined functions
- 📦 Built-in caching to eliminate redundant model invocations across queries
- ⌨️ First-class support for PyTorch, Hugging Face, YOLO, and Open AI models
- 🐍 Installable via pip and fully implemented in Python



Try it out!
------------

- `PrivateGPT <https://evadb.readthedocs.io/en/stable/source/tutorials/13-privategpt.html>`_
- `Video Question Answering using ChatGPT <https://evadb.readthedocs.io/en/stable/source/tutorials/08-chatgpt.html>`_
- `Querying PDF documents <https://evadb.readthedocs.io/en/stable/source/tutorials/12-query-pdf.html>`_
- `Analyzing traffic flow at an intersection <https://evadb.readthedocs.io/en/stable/source/tutorials/02-object-detection.html>`_
- `Examining the emotion palette of actors in a movie <https://evadb.readthedocs.io/en/stable/source/tutorials/03-emotion-analysis.html>`_
- `Classifying images based on their content <https://evadb.readthedocs.io/en/stable/source/tutorials/01-mnist.html>`_



