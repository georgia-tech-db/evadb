.. _sklearn:

Model Training with Sklearn
============================

1. Installation
---------------

To use the `Flaml Sklearn AutoML framework <https://microsoft.github.io/FLAML/docs/Examples/Integrate%20-%20Scikit-learn%20Pipeline/>`_, we need to install the extra Flaml dependency in your EvaDB virtual environment.

.. code-block:: bash

   pip install "flaml[automl]"

2. Example Query
----------------

.. code-block:: sql

   CREATE FUNCTION IF NOT EXISTS PredictRent FROM
   ( SELECT number_of_rooms, number_of_bathrooms, days_on_market, rental_price FROM HomeRentals )
   TYPE Sklearn
   PREDICT 'rental_price';

In the above query, you are creating a new customized function by training a model from the ``HomeRentals`` table using the ``Flaml Sklearn`` framework.
The ``rental_price`` column will be the target column for predication, while the rest columns from the ``SELECT`` query are the inputs.

3. Model Training Parameters
----------------------------

.. list-table:: Available Parameters
   :widths: 25 75

   * - PREDICT (**required**)
     - The name of the column we wish to predict.
   * - MODEL
     - The Sklearn models supported as of now are ``Random Forest``, ``Extra Trees Regressor`` and ``KNN``.
       You can use ``rf`` for Random Forests, ``extra_tree`` for ExtraTrees Regressor, and ``kneighbor`` for KNN.
   * - TIME_LIMIT
     - Time limit to train the model in seconds. Default: 120.
   * - TASK
     - Specify whether you want to perform ``regression`` task or ``classification`` task.
   * - METRIC
     - Specify the metric that you want to use to train your model. For e.g. for training ``regression`` tasks you could
       use the ``r2`` or ``RMSE`` metrics. For training ``classification`` tasks you could use the ``accuracy`` or ``f1_score`` metrics.
       More information about the model metrics could be found `here <https://microsoft.github.io/FLAML/docs/Use-Cases/Task-Oriented-AutoML#optimization-metric>`_

Below are the example queries specifying the aboe parameters

.. code-block:: sql

   CREATE OR REPLACE FUNCTION PredictHouseRentSklearn FROM
   ( SELECT number_of_rooms, number_of_bathrooms, days_on_market, rental_price FROM HomeRentals )
   TYPE Sklearn
   PREDICT 'rental_price'
   MODEL 'extra_tree'
   METRIC 'r2'
   TASK 'regression'
   TIME_LIMIT 180;
