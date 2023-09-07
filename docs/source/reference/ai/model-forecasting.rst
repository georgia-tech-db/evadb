Time Series Forecasting
========================

You can train a forecasting model easily in EvaDB.

.. note::

   Install `statsforecast` in your EvaDB virtual environment: ``pip install eva[forecasting]``.

First, we create a table to insert required data.

.. code-block:: sql
   
   CREATE TABLE AirData (
    unique_id TEXT(30),
    ds TEXT(30),
    y INTEGER);

   LOAD CSV 'data/forecasting/air-passengers.csv' INTO AirData;


Next, we create a function of `TYPE Forecasting`. We must enter the column name on which we wish to forecast using `predict`. Other options include `id` and `time` (they represent the unique id of the items and the time data if available).

.. code-block:: sql
   
   CREATE FUNCTION IF NOT EXISTS Forecast FROM
   (SELECT y FROM AirData)
   TYPE Forecasting
   PREDICT 'y';

This trains a forecasting model. The model can be called by providing the horizon for forecasting.

.. code-block:: sql

   SELECT Forecast(12) FROM AirData;

Here, the horizon is `12`.
