===
Concepts
===

These are some high-level concepts related to EvaDB.

If you still have questions after reading this documents,  ping us on
`our Slack <https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg>`__!

User-Defined Function (UDF) or Function
======================================

User-defined functions are thin wrappers around deep learning models. They 
allow us to use deep learning models in AI queries.

Here is an illustrative UDF for classifying MNIST images.

.. code-block:: bash

    !wget -nc https://raw.githubusercontent.com/georgia-tech-db/eva/master/evadb/udfs/mnist_image_classifier.py

.. code-block:: python

    cursor.create_udf("MnistImageClassifier", True, 'mnist_image_classifier.py')
    response = cursor.df()
    print(response)

You can use the newly registered UDF anywhere in the query!
~~~~

.. code-block:: python

    query = cursor.table("MNISTVid")
    query = query.filter("id = 30 OR id = 50 OR id = 70")
    query = query.select("data, MnistImageClassifier(data).label")
    response = query.df()