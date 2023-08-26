Image Similarity Search Pipeline using EvaDB on Images
====

In this use case, we want to search similar images based on an image provided by the user. To implement this use case, we leverage EvaDB's capability of easily expressing feature extraction pipeline. Additionaly, we also leverage EvaDB's capability of building a similarity search index and searching the index to
locate similar images through ``FAISS`` library.

For this use case, we use a reddit image dataset that can be downloaded from `Here <https://www.dropbox.com/scl/fo/fcj6ojmii0gw92zg3jb2s/h\?dl\=1\&rlkey\=j3kj1ox4yn5fhonw06v0pn7r9>`_.
We populate a table in the database that contains all images.

1. Connect to EvaDB
----

.. code-block:: python

    import evadb
    cursor = evadb.connect().cursor()

2. Register SIFT as Function
----

.. code-block:: python

    cursor.query("""
        CREATE UDF IF NOT EXISTS SiftFeatureExtractor
        IMPL  'evadb/udfs/sift_feature_extractor.py'
    """).execute()

3. Search Similar Images
----

To locate images that have similar appearance, we will first build an index based on embeddings of images.
Then, for the given image, EvaDB can find similar images by searching in the index.

Build Index using ``FAISS``
****

The below query creates a new index on the projected column ``SiftFeatureExtractor(data)`` from the ``reddit_dataset`` table.

.. code-block:: python

    cursor.query("""
        CREATE INDEX reddit_sift_image_index 
        ON reddit_dataset (SiftFeatureExtractor(data)) 
        USING FAISS
    """).execute()

Search Index for a Given Image
****

EvaDB leverages the ``ORDER BY ... LIMIT ...`` SQL syntax to retrieve the top 5 similar images.
In this example, ``Similarity(x, y)`` is a built-in function to calculate distance between ``x`` and ``y``.
In current version, ``x`` is a single tuple and ``y`` is a column that contains multiple tuples.
By default EvaDB does pairwise distance calculation between ``x`` and all tuples from ``y``.
In this case, EvaDB leverages the index that we have already built.

.. code-block:: python

    query = cursor.query("""
        SELECT name FROM reddit_dataset ORDER BY
        Similarity(
            SiftFeatureExtractor(Open('reddit-images/g1074_d4mxztt.jpg')),
            SiftFeatureExtractor(data)
        )
        LIMIT 5
    """)
    query.df()

The ``DataFrame`` contains the top 5 similar images.

.. code-block::

    +---------------------------------+
    | reddit_dataset.name             |
    |---------------------------------|
    | reddit-images/g1074_d4mxztt.jpg |
    | reddit-images/g348_d7ju7dq.jpg  |
    | reddit-images/g1209_ct6bf1n.jpg |
    | reddit-images/g1190_cln9xzr.jpg |
    | reddit-images/g1190_clna2x2.jpg |
    +---------------------------------+

Check out our `Jupyter Notebook <https://github.com/georgia-tech-db/evadb/blob/master/tutorials/11-similarity-search-for-motif-mining.ipynb>`_ for working example.
We also demonstrate more complicated features of EvaDB for similarity search.