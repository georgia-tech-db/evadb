.. _homesale-forecasting:

Home Sale Forecasting
=====================

.. raw:: html

    <embed>
    <table align="left">
    <td>
        <a target="_blank" href="https://colab.research.google.com/github/georgia-tech-db/eva/blob/staging/tutorials/16-homesale-forecasting.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run on Google Colab</a>
    </td>
    <td>
        <a target="_blank" href="https://github.com/georgia-tech-db/eva/blob/staging/tutorials/16-homesale-forecasting.ipynb"><img src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a>
    </td>
    <td>
        <a target="_blank" href="https://github.com/georgia-tech-db/eva/raw/staging/tutorials/16-homesale-forecasting.ipynb"><img src="https://www.tensorflow.org/images/download_logo_32px.png" /> Download notebook</a>
    </td>
    </table><br><br>
    </embed>

Introduction
------------

In this tutorial, we present how to use :ref:`forecasting models<forecast>` in EvaDB to predict home sale price. EvaDB makes it easy to do time series predictions using its built-in Auto Forecast function.

.. include:: ../shared/evadb.rst

.. include:: ../shared/postgresql.rst

We will assume that the input data is loaded into a ``PostgreSQL`` database. 
To load the home sales data into your database, see the complete `home sale forecasting notebook on Colab <https://colab.research.google.com/github/georgia-tech-db/eva/blob/staging/tutorials/16-homesale-forecasting.ipynb>`_.

Preview the Home Sales Data
-------------------------------------------

We use the `raw_sales.csv of the House Property Sales Time Series <https://www.kaggle.com/datasets/htagholdings/property-sales?resource=download>`_ in this usecase. The data contains five columns: postcode, price, bedrooms, datesold, and propertytype.

.. code-block:: sql

   SELECT * FROM postgres_data.home_sales LIMIT 3;

This query previews the data in the home_sales table:

.. code-block:: 

    +---------------------+------------------+---------------------+---------------------+-------------------------+
    | home_sales.postcode | home_sales.price | home_sales.bedrooms | home_sales.datesold | home_sales.propertytype |
    |---------------------|------------------|---------------------|---------------------|-------------------------|
    |                2607 |           525000 |                   4 |          2007-02-07 |                   house |
    |                2906 |           290000 |                   3 |          2007-02-27 |                   house |
    |                2905 |           328000 |                   3 |          2007-03-07 |                   house |
    +---------------------+------------------+---------------------+---------------------+-------------------------+

Train a Home Sale Forecasting Model
-----------------------------------

Let's next train a time-series forecasting model from the home_sales table using EvaDB's ``CREATE FUNCTION`` query.
Particularly, we are interested in the price of the properties that have three bedrooms and are in the postcode 2607 area.

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

In the ``home_sales`` dataset, we have two different property types, houses and units, and price gap between them are large. 
We'd like to ask EvaDB to analyze the price of houses and units independently. 
To do so, we specify the ``propertytype`` column as the ``ID `` of the time series data, which represents an identifier for the series.
Here is the query's output ``DataFrame``:

.. note::

   Go over :ref:`forecast` page on exploring all configurable paramters for the forecast model.

.. code-block:: 

   +----------------------------------------------+
   | Function HomeSaleForecast successfully added |
   +----------------------------------------------+

Predict the Home Price using the Trained Model
----------------------------------------------

Next we use the trained ``HomeSaleForecast`` to predict the home sale price for next 3 weeks.

.. code-block:: sql

   SELECT HomeSaleForecast(3);

The input of the trained model is the horizon (i.e., week in this case), the steps we want to forecast in the future. Here is the query's output ``DataFrame``:

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

We can further use ``ORDER BY`` to find out which month in the following year has the lower price.

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
