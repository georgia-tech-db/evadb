.. _ludwig:

Model Training with Ludwig
==========================

1. Installation
---------------

To use the `Ludwig framework <https://ludwig.ai/latest/>`_, we need to install the extra ludwig dependency in your EvaDB virtual environment.

.. code-block:: bash
   
   pip install evadb[ludwig]

2. Example Query
----------------

.. code-block:: sql

   CREATE OR REPLACE FUNCTION PredictHouseRent FROM
   ( SELECT sqft, location, rental_price FROM HomeRentals )
   TYPE Ludwig
   PREDICT 'rental_price'
   TIME_LIMIT 120;

In the above query, you are creating a new customized function by automatically training a model from the ``HomeRentals`` table.
The ``rental_price`` column will be the target column for predication, while ``sqft`` and ``location`` are the inputs. 

You can also simply give all other columns in ``HomeRentals`` as inputs and let the underlying AutoML framework to figure it out. Below is an example query:

.. code-block:: sql

   CREATE FUNCTION IF NOT EXISTS PredictHouseRent FROM
   ( SELECT * FROM HomeRentals )
   TYPE Ludwig
   PREDICT 'rental_price'
   TIME_LIMIT 120;

.. note::

   Check out our :ref:`homerental-predict` for working example.

3. Model Training Parameters
----------------------------

.. list-table:: Available Parameters
   :widths: 25 75

   * - PREDICT (**required**)
     - The name of the column we wish to predict.
   * - TIME_LIMIT
     - Time limit to train the model in seconds. Default: 120.
   * - TUNE_FOR_MEMORY
     - Whether to refine hyperopt search space for available host / GPU memory. Default: False.    

Below is an example query specifying the above parameters:

.. code-block:: sql

   CREATE FUNCTION IF NOT EXISTS PredictHouseRent FROM
   ( SELECT * FROM HomeRentals )
   TYPE Ludwig
   PREDICT 'rental_price'
   TIME_LIMIT 3600
   TUNE_FOR_MEMORY True;
