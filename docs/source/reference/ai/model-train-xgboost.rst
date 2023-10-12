.. _xgboost:

Model Training with XGBoost
============================

1. Installation
---------------

To use the `Flaml XGBoost AutoML framework <https://microsoft.github.io/FLAML/docs/Examples/AutoML-for-XGBoost/>`_, we need to install the extra Flaml dependency in your EvaDB virtual environment.

.. code-block:: bash

   pip install "flaml[automl] matplotlib openml"

2. Example Query
----------------

.. code-block:: sql

   CREATE FUNCTION IF NOT EXISTS PredictRent FROM
   ( SELECT number_of_rooms, number_of_bathrooms, days_on_market, rental_price FROM HomeRentals )
   TYPE XGBoost
   PREDICT 'rental_price';

In the above query, you are creating a new customized function by training a model from the ``HomeRentals`` table using the ``Flaml XGBoost`` framework.
The ``rental_price`` column will be the target column for predication, while the rest columns from the ``SELET`` query are the inputs. 
