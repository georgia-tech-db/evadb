.. _forecast:

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


Next, we create a function of `TYPE Forecasting`. We must enter the column name on which we wish to forecast using `PREDICT`.

.. code-block:: sql
   
   CREATE FUNCTION IF NOT EXISTS Forecast FROM
   (SELECT y FROM AirData)
   TYPE Forecasting
   PREDICT 'y';

This trains a forecasting model. The model can be called by providing the horizon for forecasting.

.. code-block:: sql

   SELECT Forecast(12);

Here, the horizon is `12`, which represents the forecast 12 steps into the future.


Forecast Parameters
-------------------

EvaDB's default forecast framework is `statsforecast <https://nixtla.github.io/statsforecast/>`_.

.. list-table:: Available Parameters
   :widths: 25 75

   * - PREDICT (required) 
     - The name of the column we wish to forecast.
   * - TIME
     - The name of the column that contains the datestamp, wihch should be of a format expected by Pandas, ideally YYYY-MM-DD for a date or YYYY-MM-DD HH:MM:SS for a timestamp. Please visit the `pandas documentation <https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html>`_ for details. If not provided, an auto increasing ID column will be used.
   * - ID
     - The name of column that represents an identifier for the series. If not provided, the whole table is considered as one series of data.
   * - MODEL
     - We can select one of AutoARIMA, AutoCES, AutoETS, AutoTheta. The default is AutoARIMA. Check `Automatic Forecasting <https://nixtla.github.io/statsforecast/src/core/models_intro.html#automatic-forecasting>`_ to learn details about these models.
   * - Frequency
     - A string indicating the frequency of the data. The common used ones are D, W, M, Y, which repestively represents day-, week-, month- and year- end frequency. The default value is M. Check `pandas available frequencies <https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases>`_ for all available frequencies.

Below is an example query specifying the above parameters:

.. code-block:: sql
   
   CREATE FUNCTION IF NOT EXISTS HomeRentalForecast FROM
   (SELECT saledate, ma, type FROM HomeData)
   TYPE Forecasting
   PREDICT 'ma'
   TIME 'saledate'
   ID 'type'
   MODEL 'AutoCES'
   Frequency 'W';
