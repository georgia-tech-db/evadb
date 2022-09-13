Overview
=========

|github_stars| |pypi_status| |actions_status| |documentation_status|

What is EVA?
------------

`EVA <https://github.com/georgia-tech-db/eva>`_ is a visual data management system (think MySQL for videos). It supports a declarative language similar to SQL and a wide range of commonly used  computer vision models.

What does EVA do?
-----------------

* EVA **enables querying of visual data** in user facing applications by providing a simple SQL-like interface for a wide range of commonly used computer vision models.

* EVA **improves throughput** by introducing sampling, filtering, and caching techniques.

* EVA **improves accuracy** by introducing state-of-the-art model specialization and selection algorithms.

Starting EVA
------------

.. grid:: 1 1 2 2
    :gutter: 3
    :margin: 0
    :padding: 3 4 0 0

    .. grid-item-card:: :doc:`Tutorial: Intro to EVA <tutorial/index>`
        :link: tutorial
        :link-type: doc

        A simple example of using BentoML in action. In under 10 minutes, you'll be able to serve your ML model over an HTTP API endpoint, and build a docker image that is ready to be deployed in production.

    .. grid-item-card:: :doc:`SQL Commands <sql/index>`
        :link: sql/index
        :link-type: doc

        A step-by-step tour of BentoML's components and introduce you to its philosophy. After reading, you will see what drives BentoML's design, and know what `bento` and `runner` stands for.
    
    .. grid-item-card:: :doc:`Registering UDFs <sql/index>`
        :link: sql/index
        :link-type: doc

        A step-by-step tour of BentoML's components and introduce you to its philosophy. After reading, you will see what drives BentoML's design, and know what `bento` and `runner` stands for.


.. spelling::

.. |pypi_status| image:: https://img.shields.io/pypi/v/bentoml.svg?style=flat-square
   :target: https://pypi.org/project/evadb
.. |downloads| image:: https://pepy.tech/badge/bentoml?style=flat-square
   :target: https://will add for downloads
.. |actions_status| image:: https://github.com/bentoml/bentoml/workflows/CI/badge.svg
   :target: https://github.com/bentoml/bentoml/actions
.. |documentation_status| image:: https://readthedocs.org/projects/bentoml/badge/?version=latest&style=flat-square
   :target: https://evadb.readthedocs.io/en/latest/index.html
.. |join_slack| image:: https://badgen.net/badge/Join/BentoML%20Slack/cyan?icon=slack&style=flat-square
   :target: https:/will add slack for EVA
.. |github_stars| image:: https://img.shields.io/github/stars/bentoml/BentoML?color=%23c9378a&label=github&logo=github&style=flat-square
   :target: https://github.com/georgia-tech-db/eva