User-Defined Function
====

User-defined functions (UDFs) allow us to combine SQL with deep learning models. These functions wrap around deep learning models.

Here is an illustrative UDF for classifying MNIST images.

.. code-block:: bash

    !wget -nc https://raw.githubusercontent.com/georgia-tech-db/eva/master/eva/udfs/mnist_image_classifier.py

.. code-block:: python

    cursor.execute("""DROP UDF IF EXISTS MnistImageClassifier;""")
    response = cursor.fetch_all()
    print(response)

    cursor.execute("""CREATE UDF IF NOT EXISTS MnistImageClassifier
                      INPUT  (data NDARRAY (3, 28, 28))
                      OUTPUT (label TEXT(2))
                      TYPE  Classification
                      IMPL  'mnist_image_classifier.py';
                    """)
    response = cursor.fetch_all()
    print(response)

Run a query using the newly registered UDF!
~~~~

.. code-block:: python

    cursor.execute("""SELECT data, MnistImageClassifier(data).label 
                      FROM MNISTVideoTable
                      WHERE id = 30;""")
    response = cursor.fetch_all()

Visualize the output
~~~~

The output of the query is `visualized in the notebook <https://evadb.readthedocs.io/en/stable/source/tutorials/01-mnist.html#visualize-output-of-query-on-the-video>`_.
