Exploratory Video Analytics
===================================================

|pypi_status| |CI Status| |Coverage Status| |License| |documentation_status| |Discuss| |Python Versions|

What is EVA?
------------

`EVA <https://github.com/georgia-tech-db/eva>`_ is a new database system tailored for video analytics -- think PostgreSQL for videos. It supports a SQL-like language for querying videos (e.g., finding frames in a movie with your favorite actor or finding touchdowns in a football game). It comes with a wide range of commonly used computer vision models.

Key Features
------------

1. With EVA, you can **easily combine SQL and deep learning models to build next-generation database applications**. EVA treats deep learning models as user-defined functions similar to built-in functions like SUM().

2. EVA is **extensible by design**. You can write an **user-defined function** (UDF) that wraps arounds your custom deep learning model. In fact, all the built-in models that are included in EVA are written as user-defined functions.

3. EVA comes with a collection of **built-in sampling, caching, and filtering optimizations** inspired by time-tested relational database systems. These optimizations help **speed up queries on large datasets and save money spent on model inference**.

Next Steps
------------

.. grid:: 1 1 2 2
    :gutter: 3
    :margin: 0
    :padding: 3 4 0 0

    .. grid-item-card:: :doc:`Tutorial:  to EVA <source/tutorials/overview>`
        :link: source/overview/installation
        :link-type: doc
        
        Getting Started

    .. grid-item-card:: :doc:`SQL Commands <source/reference/evaql>`
        :link: source/reference/evaql
        :link-type: doc
        
        Query Language
    
    .. grid-item-card:: :doc:`Registering UDFs <source/reference/udf>`
        :link: source/reference/udf
        :link-type: doc
        
        User Defined Functions


.. spelling::

.. |pypi_status| image:: https://img.shields.io/pypi/v/evadb.svg
   :target: https://pypi.org/project/evadb
.. |License| image:: https://img.shields.io/badge/license-Apache%202-brightgreen.svg?logo=apache
   :target: https://github.com/georgia-tech-db/eva/blob/master/LICENSE.txt
.. |Discuss| image:: https://img.shields.io/badge/-Discuss!-blueviolet
   :target: https://github.com/georgia-tech-db/eva/discussions
.. |Python Versions| image:: https://img.shields.io/badge/Python--versions-3.7+-brightgreen
   :target: https://github.com/georgia-tech-db/eva
