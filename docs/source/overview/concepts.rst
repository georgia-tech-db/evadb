=========
Concepts
=========

These are some high-level concepts related to EvaDB.

If you still have questions after reading this documents,  ping us on
`our Slack <https://join.slack.com/t/eva-db/shared_invite/zt-1i10zyddy-PlJ4iawLdurDv~aIAq90Dg>`__!

User-Defined Function (UDF) or Function
======================================

User-defined functions are thin wrappers around deep learning models. They 
allow us to use deep learning models in AI queries.

Here is an illustrative UDF for classifying MNIST images.

.. code-block:: bash

    !wget -nc https://raw.githubusercontent.com/georgia-tech-db/evadb/master/evadb/udfs/mnist_image_classifier.py

.. code-block:: python

    cursor.create_function("MnistImageClassifier", True, 'mnist_image_classifier.py')
    response = cursor.df()
    print(response)

That's it! You can now use the newly registered UDF anywhere in the query -- in the ``select`` or ``filter`` calls.

.. code-block:: python

    query = cursor.table("MNISTVideo")
    query = query.filter("id = 30 OR id = 50 OR id = 70")

    # Here, we are selecting the output of the function
    query = query.select("data, MnistImageClassifier(data).label")
    response = query.df()

.. code-block:: python

    query2 = cursor.table("MNISTVideo")

    # Here, we are also filtering based on the output of the function
    query2 = query2.filter("MnistImageClassifier(data).label = '6' AND id < 10")
    query2 = query2.select("data, MnistImageClassifier(data).label")
    response = query2.df()