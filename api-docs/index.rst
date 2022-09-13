Exploratory Video Analytics
===================================================

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

    .. grid-item-card:: :doc:`Tutorial: Intro to EVA <source/tutorials/tutorials>`
        :link: source/tutorials/tutorials
        :link-type: doc
        :class-card: content-cards

        A simple example of using EVA.

    .. grid-item-card:: :doc:`SQL Commands <source/reference/index>`
        :link: source/reference/index
        :link-type: doc
        :class-card: content-cards

        All SQL commands supported by EVA.
    
    .. grid-item-card:: :doc:`Registering UDFs <source/reference/udf>`
        :link: source/reference/udf
        :link-type: doc
        :class-card: content-cards

        A step-by-step tour of creating custom User Defined Functions for EVA.




.. spelling::

.. .. |pypi_status| image:: https://img.shields.io/pypi/v/bentoml.svg?style=flat-square
..    :target: https://pypi.org/project/evadb
.. .. |downloads| image:: https://pepy.tech/badge/bentoml?style=flat-square
..    :target: https://will add for downloads
.. .. |actions_status| image:: https://github.com/bentoml/bentoml/workflows/CI/badge.svg
..    :target: https://github.com/bentoml/bentoml/actions
.. .. |documentation_status| image:: https://readthedocs.org/projects/bentoml/badge/?version=latest&style=flat-square
..    :target: https://evadb.readthedocs.io/en/latest/index.html
.. .. |join_slack| image:: https://badgen.net/badge/Join/BentoML%20Slack/cyan?icon=slack&style=flat-square
..    :target: https:/will add slack for EVA
.. .. |github_stars| image:: https://img.shields.io/github/stars/bentoml/BentoML?color=%23c9378a&label=github&logo=github&style=flat-square
..    :target: https://github.com/georgia-tech-db/eva