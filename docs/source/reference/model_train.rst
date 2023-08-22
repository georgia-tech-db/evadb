Model Train and Finetune
====

1. You can train a predication model easily in EvaDB

.. note::

   Install Ludwig in your EvaDB virtual environment: ``pip install evadb[ludwig]``.

.. code-block:: sql

   CREATE UDF IF NOT EXISTS PredictHouseRent FROM
   (SELECT * FROM HomeRentals)
   TYPE Ludwig
   'predict' 'rental_price'
   'time_limit' 120;

In the above query, you are creating a new customized UDF by automatically training a model from the `HomeRentals` table. The `rental_price` column will be the target column for predication, while all other columns in `HomeRentals` are the inputs. 

.. note::

   Check :ref:`create-udf-train` for available configurations for training models.

2. After training completes, you can use the `PredictHouseRent` like all other UDFs in EvaDB

.. code-block:: sql

   CREATE PredictHouseRent(*) FROM HomeRentals;

Check out our `Integration Tests <https://github.com/georgia-tech-db/evadb/blob/master/test/integration_tests/test_model_train.py>`_ for working example.


