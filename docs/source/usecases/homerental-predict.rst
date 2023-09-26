.. _homerental-predict:

Home Rental Prediction
=======================

.. raw:: html

    <embed>
    <table align="left">
    <td>
        <a target="_blank" href="https://colab.research.google.com/github/georgia-tech-db/eva/blob/staging/tutorials/17-home-rental-prediction.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run on Google Colab</a>
    </td>
    <td>
        <a target="_blank" href="https://github.com/georgia-tech-db/eva/blob/staging/tutorials/17-home-rental-prediction.ipynb"><img src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a>
    </td>
    <td>
        <a target="_blank" href="https://github.com/georgia-tech-db/eva/raw/staging/tutorials/17-home-rental-prediction.ipynb"><img src="https://www.tensorflow.org/images/download_logo_32px.png" /> Download notebook</a>
    </td>
    </table><br><br>
    </embed>

Introduction
------------

In this tutorial, we present how to use :ref:`Prediction AI Engines<ludwig>` in EvaDB to predict home rental prices. EvaDB makes it easy to do predictions using its built-in AutoML engines with your existing databases.

.. include:: ../shared/evadb.rst

.. include:: ../shared/postgresql.rst

We will assume that the input data is loaded into a ``PostgreSQL`` database. 
To load the home rental data into your database, see the complete `home rental prediction notebook on Colab <https://colab.research.google.com/github/georgia-tech-db/eva/blob/staging/tutorials/17-home-rental-prediction.ipynb>`_.

Preview the Home Sales Data
-------------------------------------------

We use the `home rental data <https://www.dropbox.com/scl/fi/gy2682i66a8l2tqsowm5x/home_rentals.csv?rlkey=e080k02rv5205h4ullfjdr8lw&raw=1>`_ in this usecase. The data contains eight columns: ``number_of_rooms``, ``number_of_bathrooms``, ``sqft``, ``location``, ``days_on_market``, ``initial_price``, ``neighborhood``, and ``rental_price``.

.. code-block:: sql

   SELECT * FROM postgres_data.home_rentals LIMIT 3;

This query previews the data in the home_rentals table:

.. code-block:: 

    +------------------------------+----------------------------------+-------------------+-----------------------+-----------------------------+----------------------------+---------------------------+---------------------------+
    | home_rentals.number_of_rooms | home_rentals.number_of_bathrooms | home_rentals.sqft | home_rentals.location | home_rentals.days_on_market | home_rentals.initial_price | home_rentals.neighborhood | home_rentals.rental_price |
    |------------------------------|----------------------------------|-------------------|-----------------------|-----------------------------|----------------------------|---------------------------|---------------------------|
    |                            1 |                                1 |               674 |                  good |                           1 |                       2167 |                  downtown |                      2167 |
    |                            1 |                                1 |               554 |                  poor |                          19 |                       1883 |                  westbrae |                      1883 |
    |                            0 |                                1 |               529 |                 great |                           3 |                       2431 |                south_side |                      2431 | 
    +------------------------------+----------------------------------+-------------------+-----------------------+-----------------------------+----------------------------+---------------------------+---------------------------+

Train a Home Rental Prediction Model
-------------------------------------

Let's next train a prediction model from the home_rental table using EvaDB's ``CREATE FUNCTION`` query.
We will use the built-in :ref:`Ludwig<ludwig>` engine for this task.

.. code-block:: sql
  
  CREATE OR REPLACE FUNCTION PredictHouseRent FROM
  ( SELECT * FROM postgres_data.home_rental )
  TYPE Ludwig
  PREDICT 'rental_price'
  TIME_LIMIT 3600;

In the above query, we use all the columns (except ``rental_price``) from ``home_rental`` table to predict the ``rental_price`` column.
We set the training time out to be 3600 seconds.

.. note::

   Go over :ref:`ludwig` page on exploring all configurable paramters for the model training frameworks.

.. code-block:: 

   +----------------------------------------------+
   | Function PredictHouseRent successfully added |
   +----------------------------------------------+

Predict the Home Rental Price using the Trained Model
-----------------------------------------------------

Next we use the trained ``PredictHouseRent`` to predict the home rental price.

.. code-block:: sql

   SELECT PredictHouseRent(*) FROM postgres_data.home_rentals LIMIT 3;

We use ``*`` to simply pass all columns into the ``PredictHouseRent`` function.

.. code-block::

   +-------------------------------------------+
   | predicthouserent.rental_price_predictions |
   +-------------------------------------------+
   |                               2087.763672 |
   |                               1793.570190 |
   |                               2346.319824 |
   +-------------------------------------------+

We have the option to utilize a ``LATERAL JOIN`` to compare the actual rental prices in the ``home_rentals`` dataset with the predicted rental prices generated by the trained model, ``PredictHouseRent``.

.. code-block:: sql

   SELECT rental_price, predicted_rental_price
   FROM postgres_data.home_rentals
   JOIN LATERAL PredictHouseRent(*) AS Predicted(predicted_rental_price)
   LIMIT 3;

Here is the query's output:

.. code-block::

   +---------------------------+----------------------------------+
   | home_rentals.rental_price | Predicted.predicted_rental_price |
   +---------------------------+----------------------------------+
   |                      2167 |                      2087.763672 |
   |                      1883 |                      1793.570190 |
   |                      2431 |                      2346.319824 |
   +------------------ --------+----------------------------------+
      
.. include:: ../shared/footer.rst
