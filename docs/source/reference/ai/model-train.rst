.. _predict:

Training and Finetuning
========================

1. You can train a predication model easily in EvaDB

.. note::

   Install Ludwig in your EvaDB virtual environment: ``pip install evadb[ludwig]``.

.. code-block:: sql

   CREATE FUNCTION IF NOT EXISTS PredictHouseRent FROM
   ( SELECT sqft, location, rental_price FROM HomeRentals )
   TYPE Ludwig
   PREDICT 'rental_price'
   TIME_LIMIT 120;

In the above query, you are creating a new customized function by automatically training a model from the `HomeRentals` table. The `rental_price` column will be the target column for predication, while `sqft` and `location` are the inputs. 

You can also simply give all other columns in `HomeRentals` as inputs and let the underlying automl framework to figure it out. Below is an example query:

.. code-block:: sql

   CREATE FUNCTION IF NOT EXISTS PredictHouseRent FROM
   ( SELECT * FROM HomeRentals )
   TYPE Ludwig
   PREDICT 'rental_price'
   TIME_LIMIT 120;

2. After training completes, you can use the `PredictHouseRent` like all other functions in EvaDB

.. code-block:: sql

   CREATE PredictHouseRent(sqft, location) FROM HomeRentals;

You can also simply give all columns in `HomeRentals` as inputs for inference. The customized function with the underlying model can figure out the proper inference columns via the training columns.

.. code-block:: sql

   CREATE PredictHouseRent(*) FROM HomeRentals;

Check out our `Integration Tests <https://github.com/georgia-tech-db/evadb/blob/staging/test/integration_tests/long/test_model_train.py>`_ for working example.


