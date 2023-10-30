.. _xgboost:

Model Training with XGBoost
============================

1. Installation
---------------

To use the `Flaml XGBoost AutoML framework <https://microsoft.github.io/FLAML/docs/Examples/AutoML-for-XGBoost/>`_, we need to install the extra Flaml dependency in your EvaDB virtual environment.

.. code-block:: bash

   pip install "flaml[automl]"

2. Example Query
----------------

.. code-block:: sql

   CREATE FUNCTION IF NOT EXISTS PredictRent FROM
   ( SELECT number_of_rooms, number_of_bathrooms, days_on_market, rental_price FROM HomeRentals )
   TYPE XGBoost
   PREDICT 'rental_price';

In the above query, you are creating a new customized function by training a model from the ``HomeRentals`` table using the ``Flaml XGBoost`` framework.
The ``rental_price`` column will be the target column for predication, while the rest columns from the ``SELECT`` query are the inputs.

3. Model Training Parameters
----------------------------

.. list-table:: Available Parameters
   :widths: 25 75

   * - PREDICT (**required**)
     - The name of the column we wish to predict.
   * - TIME_LIMIT
     - Time limit to train the model in seconds. Default: 120.
   * - TASK
     - Specify whether you want to perform ``regression`` task or ``classification`` task.
   * - METRIC
     - Specify the metric that you want to use to train your model. For e.g. for training ``regression`` tasks you could
       use the ``r2`` or ``RMSE`` metrics. For training ``classification`` tasks you could use the ``accuracy`` or ``f1_score`` metrics.

Below are the example queries specifying the aboe parameters

.. code-block:: sql

   CREATE FUNCTION IF NOT EXISTS PredictRent FROM
   ( SELECT number_of_rooms, number_of_bathrooms, days_on_market, rental_price FROM HomeRentals )
   TYPE XGBoost
   PREDICT 'rental_price'
   TIME_LIMIT 180
   METRIC 'r2'
   TASK 'regression';

.. code-block:: sql

   CREATE FUNCTION IF NOT EXISTS PredictEmployee FROM
   ( SELECT payment_tier, age, gender, experience_in_current_domain, leave_or_not FROM Employee )
   TYPE XGBoost
   PREDICT 'leave_or_not'
   TIME_LIMIT 180
   METRIC 'accuracy'
   TASK 'classification';
