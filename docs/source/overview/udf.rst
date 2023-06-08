User-Defined Function
====

User-defined functions (UDFs) allow us to combine SQL with deep learning models. These functions wrap around deep learning models.

Here is an illustrative UDF for classifying MNIST images.

.. code-block:: bash

    !wget -nc https://raw.githubusercontent.com/georgia-tech-db/eva/master/evadb/udfs/mnist_image_classifier.py

.. code-block:: python

    cursor.execute("""DROP UDF IF EXISTS MnistImageClassifier;""")
    response = cursor.df()
    print(response)

    cursor.create_udf("MnistImageClassifier", True, 'mnist_image_classifier.py')
    response = cursor.df()
    print(response)

Run a query using the newly registered UDF!
~~~~

.. code-block:: python

    query = cursor.table("MNISTVid")
    query = query.filter("id = 30 OR id = 50 OR id = 70")
    query = query.select("data, MnistImageClassifier(data).label")
    response = query.df()