.. _image classification:

Image Classification Pipeline using EvaDB
=========================================

Assume the database has loaded a video ``mnist_video``.

1. Connect to EvaDB
-------------------

.. code-block:: python

    import evadb
    cursor = evadb.connect().cursor()

2. Register Image Classification Model as a Function in SQL
-----------------------------------------------------------

Create an image classification function from python source code.

.. code-block:: python

    query = cursor.query("""
        CREATE UDF IF NOT EXISTS MnistImageClassifier 
        IMPL 'evadb/udfs/mnist_image_classifier.py';
    """).execute()

3. Execute Image Classification through SQL
-------------------------------------------

After the function is registered to EvaDB system, it can be directly called and used in SQL query.

.. tab-set::
    
    .. tab-item:: Python

        .. code-block:: python

            query = cursor.table("mnist_video").select("MnistImageClassifier(data).label")
            
            # Get results in a DataFrame.
            query.df()


    .. tab-item:: SQL 

        .. code-block:: sql

            SELECT MnistImageClassifier(data).label FROM mnist_video;

    

The result contains a projected ``label`` column, which indicates the digit of a particular frame.

.. code-block:: 

    +------------------------------+
    |   mnistimageclassifier.label |
    |------------------------------|
    |                            6 |
    |                            6 |
    |                            6 |
    |                            6 |
    |                            6 |
    |                            6 |
    |                            4 |
    |                            4 |

    ... ...

4. Optional: Process Only Segments of Videos based on Conditions
-----------------------------------------------------------------

Like normal SQL, you can also specify conditions to filter out some frames of the video.

.. tab-set::
    
    .. tab-item:: Python

        .. code-block:: python

            query = cursor.table("mnist_video") \
                        .filter("id < 2") \
                        .select("MnistImageClassifier(data).label")
            
            # Return results in a DataFrame.
            query.df()

    .. tab-item:: SQL

        .. code-block:: sql

            SELECT MnistImageClassifier(data).label FROM mnist_video 
                WHERE id < 2


Now, the ``DataFrame`` only contains 2 rows after filtering.

.. code-block:: 

    +------------------------------+
    |   mnistimageclassifier.label |
    |------------------------------|
    |                            6 |
    |                            6 |
    +------------------------------+

Check out our `Jupyter Notebook <https://github.com/georgia-tech-db/evadb/blob/master/tutorials/01-mnist.ipynb>`_ for working example.
