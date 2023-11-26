.. _sklearn:

Model Training with Sklearn
============================

1. Installation
---------------

To use the `Sklearn framework <https://scikit-learn.org/stable/>`_, we need to install the extra sklearn dependency in your EvaDB virtual environment.

.. code-block:: bash
   
   pip install evadb[sklearn]

2. Example Query
----------------

.. code-block:: sql

   CREATE OR REPLACE FUNCTION PredictHouseRent FROM
   ( SELECT number_of_rooms, number_of_bathrooms, days_on_market, rental_price FROM HomeRentals )
   TYPE Sklearn
   PREDICT 'rental_price';

In the above query, you are creating a new customized function by training a model from the ``HomeRentals`` table using the ``Sklearn`` framework.
The ``rental_price`` column will be the target column for predication, while the rest columns from the ``SELECT`` query are the inputs. 
