.. _guide-getstarted:

User-Defined Functions (UDF)
====

User-defined functions allow us to combine SQL with deep learning models. These functions wrap around deep learning models.

Download an illustrative user-defined function for classifying MNIST images.

.. code-block:: bash

    !wget -nc https://raw.githubusercontent.com/georgia-tech-db/eva/master/tutorials/apps/mnist/eva_mnist_udf.py

.. code-block:: python

    cursor.execute("""CREATE UDF IF NOT EXISTS MnistCNN
                      INPUT  (data NDARRAY (3, 28, 28))
                      OUTPUT (label TEXT(2))
                      TYPE  Classification
                      IMPL  'eva_mnist_udf.py';
                    """)
    response = cursor.fetch_all()
    print(response)

Run a query using the newly registered UDF!
~~~~

.. code-block:: python

    cursor.execute("""SELECT data, MnistCNN(data).label 
                      FROM MNISTVideoTable
                      WHERE id = 30;""")
    response = cursor.fetch_all()

Visualize the output
~~~~

The output of the query is `visualized in the notebook <https://evadb.readthedocs.io/en/stable/source/tutorials/01-mnist.html#visualize-output-of-query-on-the-video>`_.
