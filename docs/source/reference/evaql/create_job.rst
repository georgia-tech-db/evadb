CREATE JOB
===============

.. _create-function:

The CREATE JOB statement allows us to create recurring or one-time jobs in EvaDB. These jobs can be associated with multiple queries, 
all of which will be executed sequentially every time the created job is triggered according to the assigned schedule.


.. code-block:: sql

    CREATE JOB [IF NOT EXISTS] <job_name> AS {
        <job_queries>...
    }
    [START <start_time>]
    [END <end_time>]
    [EVERY <repeat_period> <repeat_unit>]

* There can be multiple queries defined per job.
* The START parameter denotes the first trigger time of the job. The default value is the job creation time.
* The END parameter denotes the last trigger time of the job. The job becomes inactive after this time. If no end value is provided, a recurring job never ends.
* The EVERY parameter can be used to specify the repeat frequency of the jobs. The repeat period is expected to be a positive integer, and accepted values for the repeat unit are "minute", "minutes", "min", "hour", "hours", "day", "days", "week", "weeks", "month", "months".


Examples
~~~~~~~~

.. code:: text

    CREATE JOB forecasting_job AS {
        CREATE OR REPLACE FUNCTION HomeSalesForecast FROM
            ( SELECT * FROM postgres_data.home_sales )
        TYPE Forecasting
        PREDICT 'price';
        SELECT HomeSalesForecast(10);
    }
    START '2023-04-01 01:10:00'
    END '2023-05-01'
    EVERY 1 week;

