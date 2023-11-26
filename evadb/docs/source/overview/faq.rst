Frequently Asked Questions
==========================

.. _faq:

Here are some frequently asked questions that we have seen pop up for EvaDB.

.. note::

    Have another question or want to give feedback? Ask us on `Slack <https://evadb.ai/community>`__!

Why am I not able to install EvaDB?
-----------------------------------

Ensure that the Python interpreter's version is >= `3.9`. 

.. note::

    If you are using the `evadb[ray]` installation option, ensure that the Python  version is <= `3.10` due to a `Ray issue <https://github.com/autogluon/autogluon/issues/2687>`_. Follow `these instructions <https://github.com/ray-project/ray/issues/33039>`_ to install `ray`.


Where does EvaDB store all the data?
------------------------------------

By default, EvaDB connects to **existing** data sources like SQL database systems. It stores all the meta-data (i.e., data about data sources) in a local folder named ``evadb_data``. Deleting this folder will reset EvaDB's state and lead to data loss.

Why do I see no output from the server?
---------------------------------------

If a query runs a complex AI task (e.g., sentiment analysis) on a large table, the query is expected to take a non-trivial amount of time to finish. You can check the status of the server by running ``top`` or ``pgrep``:

.. code-block:: bash

    top
    pgrep evadb_server

