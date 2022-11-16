Exploratory Video Analytics
===================================================

|pypi_status| |CI Status| |Coverage Status| |License| |documentation_status| |Discuss| |Python Versions|

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
        

        A simple example of using EVA.

    .. grid-item-card:: :doc:`SQL Commands <source/reference/index>`
        :link: source/reference/index
        :link-type: doc
        

        All SQL commands supported by EVA.
    
    .. grid-item-card:: :doc:`Registering UDFs <source/reference/udf>`
        :link: source/reference/udf
        :link-type: doc
        

        A step-by-step tour of creating custom User Defined Functions for EVA.




.. spelling::

.. |pypi_status| image:: https://img.shields.io/pypi/v/evadb.svg
   :target: https://pypi.org/project/evadb
.. |CI Status| image:: https://circleci.com/gh/georgia-tech-db/eva.svg?style=svg
   :target: https://circleci.com/gh/georgia-tech-db/eva
.. |Coverage Status| image:: https://coveralls.io/repos/github/georgia-tech-db/eva/badge.svg?branch=master
   :target: https://coveralls.io/github/georgia-tech-db/eva?branch=master
.. |License| image:: https://img.shields.io/badge/license-Apache%202-brightgreen.svg?logo=apache
    :target: https://github.com/georgia-tech-db/eva/blob/master/LICENSE.txt
.. |documentation_status| image:: https://readthedocs.org/projects/exvian/badge/?version=latest
   :target: https://evadb.readthedocs.io/en/latest/index.html
.. |Discuss| image:: https://img.shields.io/badge/-Discuss!-blueviolet
   :target: https://github.com/georgia-tech-db/eva/discussions
.. |Python Versions| image:: https://img.shields.io/badge/Python--versions-3.7+-brightgreen
   :target: https://github.com/georgia-tech-db/eva
