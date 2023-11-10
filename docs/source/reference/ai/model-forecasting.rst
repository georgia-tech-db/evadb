.. _forecast:

Time Series Forecasting
========================

A Time Series is a series of data points recorded at different time intervals. Time series forecasting involves estimating future values of a time series by analyzing historical data.
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
   HORIZON 12
   PREDICT 'y';

This trains a forecasting model. The model can be called by providing the horizon for forecasting.

.. code-block:: sql

   SELECT Forecast();


Forecast Parameters
-------------------

EvaDB's default forecast framework is `statsforecast <https://nixtla.github.io/statsforecast/>`_.

.. list-table:: Available Parameters
   :widths: 25 75

   * - PREDICT (str, required) 
     - The name of the column we wish to forecast.
   * - HORIZON (int, required) 
     - The number of steps into the future we wish to forecast.
   * - TIME (str, default: 'ds')
     - The name of the column that contains the datestamp, which should be of a format expected by Pandas, ideally YYYY-MM-DD for a date or YYYY-MM-DD HH:MM:SS for a timestamp. Please visit the `pandas documentation <https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html>`_ for details. If relevant column is not found, an auto increasing ID column will be used.
   * - ID (str, default: 'unique_id')
     - The name of column that represents an identifier for the series. If relevant column is not found, the whole table is considered as one series of data.
   * - LIBRARY (str, default: 'statsforecast')
     - We can select one of `statsforecast` (default) or `neuralforecast`. `statsforecast` provides access to statistical forecasting methods, while `neuralforecast` gives access to deep-learning based forecasting methods.
   * - MODEL (str, default: 'ARIMA')
     - If LIBRARY is `statsforecast`, we can select one of ARIMA, ting, ETS, Theta. The default is ARIMA. Check `Automatic Forecasting <https://nixtla.mintlify.app/statsforecast/index.html#automatic-forecasting>`_ to learn details about these models. If LIBRARY is `neuralforecast`, we can select one of NHITS or NBEATS. The default is NBEATS. Check `NBEATS docs <https://nixtla.github.io/neuralforecast/models.nbeats.html>`_ for details.
   * - AUTO (str, default: 'T')
     - If set to 'T', it enables automatic hyperparameter optimization. Must be set to 'T' for `statsforecast` library. One may set this parameter to `false` if LIBRARY is `neuralforecast` for faster (but less reliable) results.
   * - CONF (int, default: 90)
     - Sets the confidence interval in percentage for the forecast. Must be a number between 0 and 100. The lower and upper bounds of the confidence interval are returned in two separate columns, named as the PREDICT column with `-lo` and `-hi` suffixes.
   * - FREQUENCY (str, default: 'auto')
     - A string indicating the frequency of the data. The common used ones are D, W, M, Y, which respectively represents day-, week-, month- and year- end frequency. The default value is M. Check `pandas available frequencies <https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases>`_ for all available frequencies. If it is not provided, the frequency is attempted to be determined automatically.
   * - METRICS (str, default: 'True')
     - Compute NRMSE by performing cross-validation. It is `False` by default if `LIBRARY` is `neuralforecast` as it can take an extensively long time. The metrics are logged locally.

.. note::

    If columns other than the ones required as mentioned above are passed while creating the function, they will be treated as exogenous variables if LIBRARY is `neuralforecast`. Otherwise, they would be ignored.


.. note::
  
   `Forecasting` function also logs suggestions. Logged information, such as metrics and suggestions, is sent to STDOUT by default. If you wish not to print it, please send `FALSE` as an optional argument while calling the function. Eg. `SELECT Forecast(FALSE);`


Below is an example query specifying the above parameters:

.. code-block:: sql
   
   CREATE FUNCTION IF NOT EXISTS HomeRentalForecast FROM
   (SELECT saledate, ma, type FROM HomeData)
   TYPE Forecasting
   HORIZON 12
   PREDICT 'ma'
   TIME 'saledate'
   ID 'type'
   Frequency 'W';

Below is an example query with `neuralforecast` with `trend` column as exogenous and without automatic hyperparameter optimization:

.. code-block:: sql
   
    CREATE FUNCTION AirPanelForecast FROM
    (SELECT unique_id, ds, y, trend FROM AirDataPanel)
    TYPE Forecasting
    HORIZON 12
    PREDICT 'y'
    LIBRARY 'neuralforecast'
    AUTO 'f'
    FREQUENCY 'M';
