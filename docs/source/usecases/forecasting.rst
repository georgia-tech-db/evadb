.. _homesale-forecasting:

Home Sale Forecasting
=====================

.. raw:: html

    <embed>
    <table align="left">
    <td>
        <a target="_blank" href="https://colab.research.google.com/github/georgia-tech-db/eva/blob/staging/tutorials/16-homesale-forecasting.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" width="24px" /> Run on Google Colab</a>
    </td>
    <td>
        <a target="_blank" href="https://github.com/georgia-tech-db/eva/blob/staging/tutorials/16-homesale-forecasting.ipynb"><img src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" width="24px" /> View source on GitHub</a>
    </td>
    <td>
        <a target="_blank" href="https://github.com/georgia-tech-db/eva/raw/staging/tutorials/16-homesale-forecasting.ipynb"><img src="https://www.tensorflow.org/images/download_logo_32px.png" width="24px" /> Download notebook</a>
    </td>
    </table><br><br>
    </embed>

Introduction
------------

In this tutorial, we present how to create and train a machine learning model for forecasting the sale price of a home using the built-in :ref:`Forecasting AI Engines<forecast>` in EvaDB. EvaDB makes it easy to do forecasting queries over data in your database using its built-in ``Forecasting`` engines.

.. include:: ../shared/evadb.rst

.. include:: ../shared/postgresql.rst

We will assume that the input data is loaded into a ``PostgreSQL`` database. 
To load the home sales dataset into your database, see the complete `home sale forecasting notebook on Colab <https://colab.research.google.com/github/georgia-tech-db/eva/blob/staging/tutorials/16-homesale-forecasting.ipynb>`_.

Preview the Home Sale Price Data
--------------------------------

We use the `House Property Sales Time Series <https://www.kaggle.com/datasets/htagholdings/property-sales?resource=download>`_ dataset from Kaggle in this tutorial. The dataset (``raw_sales.csv``) contains five columns: 
``postcode``, ``price``, ``bedrooms``, ``datesold``, and ``propertytype``.

.. code-block:: sql

   SELECT * 
   FROM postgres_data.home_sales 
   LIMIT 3;

This query presents a subset of the dataset in the ``home_sales`` table:

.. code-block:: 

    +---------------------+------------------+---------------------+---------------------+-------------------------+
    | home_sales.postcode | home_sales.price | home_sales.bedrooms | home_sales.datesold | home_sales.propertytype |
    |---------------------|------------------|---------------------|---------------------|-------------------------|
    |                2607 |           525000 |                   4 |          2007-02-07 |                   house |
    |                2906 |           290000 |                   3 |          2007-02-27 |                   house |
    |                2905 |           328000 |                   3 |          2007-03-07 |                   house |
    +---------------------+------------------+---------------------+---------------------+-------------------------+

Train a Forecasting Model
-------------------------

Let's next train a time-series forecasting model over the ``home_sales`` table using EvaDB's ``CREATE FUNCTION`` statement. In particular, we are interested in forecasting the price of homes with three bedrooms in the 2607 ``postcode``.

.. code-block:: sql

  CREATE FUNCTION IF NOT EXISTS HomeSaleForecast FROM
  (
      SELECT propertytype, datesold, price
      FROM postgres_data.home_sales
      WHERE bedrooms = 3 AND postcode = 2607
  )
  TYPE Forecasting
  PREDICT 'price'
  TIME 'datesold'
  ID 'propertytype'
  FREQUENCY 'W';

This query returns the trained model:

.. code-block:: 

   +----------------------------------------------+
   | Function HomeSaleForecast successfully added |
   +----------------------------------------------+

.. note::

   The :ref:`forecast` page lists all the configurable parameters for the forecasting model.

In the ``home_sales`` dataset, we have two different types of properties -- houses and units, and price gap between them is large. To get better forecasts,
we specify the ``propertytype`` column as the ``ID`` of the time series data.
This denotes the identifier for the series and allows EvaDB to forecast the prices of houses and units independently.

Forecast using the Trained Model
--------------------------------

Next we use the trained ``HomeSaleForecast`` model to predict the home sale price for next 3 months. The model takes the ``horizon`` as input during prediction. The ``horizon`` denotes the steps in time over which we want to forecast in the future. In this query, the ``horizon`` is 3 months.

.. code-block:: sql

   SELECT HomeSaleForecast(3);

The query returns the forecasted prices of the properties:

.. code-block::

   +-------------------------------+---------------------------+------------------------+
   | homesaleforecast.propertytype | homesaleforecast.datesold | homesaleforecast.price |
   +-------------------------------+---------------------------+------------------------+
   |                         house |                2019-07-21 |                 766572 |
   |                         house |                2019-07-28 |                 766572 |
   |                         house |                2019-08-04 |                 766572 |
   |                          unit |                2018-12-23 |                 417229 |
   |                          unit |                2018-12-30 |                 409601 |
   |                          unit |                2019-01-06 |                 402112 |
   +-------------------------------+---------------------------+------------------------+

We may use ``ORDER BY`` to find out which month in the following year has the lowest price.

.. code-block:: sql

   SELECT * 
   FROM (SELECT HomeSaleForecast(12)) AS HomeSale
   ORDER BY price
   LIMIT 1;

Here is the query's output:

.. code-block::

   +-----------------------+-------------------+----------------+
   | HomeSale.propertytype | HomeSale.datesold | HomeSale.price |
   +-----------------------+-------------------+----------------+
   |                  unit |        2019-03-10 |         340584 |
   +-----------------------|-------------------|----------------|
   
.. include:: ../shared/footer.rst

.. include:: ../shared/designs/design11.rst