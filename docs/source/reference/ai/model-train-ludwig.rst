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

4. Using EvaDB with Common Machine Learning Techniques 
----------------
One of the most common machine learning techniques is feature selection, the process of choosing a smaller subset of features in order to improve efficiency when training the model. As long as the most important features are chosen, the model's runtime can be vastly improved without compromising efficacy. With EvaDB, feature selection can be easily implemented by simply choosing which columns to use when create the prediction function, as shown in an earlier example: 

.. code-block:: sql

   CREATE OR REPLACE FUNCTION PredictHouseRent FROM
   ( SELECT sqft, location, rental_price FROM HomeRentals )
   TYPE Ludwig
   PREDICT 'rental_price'
   TIME_LIMIT 120;

The slightly harder task is judging how effective a model is at predicting a certain value. Accuracy is one metric commonly used to judge ML models. An example of how accuracy can be calculated for our House Rent Predictor is shown below: 

-- 

The user can now test various combinations of features in order to determine which results in the best model. But there is a downside to calculating accuracy this way. Because the testing data is the same as the training data, it is difficult to judge if the model is too highly tuned to its training data, which will result in it not working as well when testing on independent data. 

Cross-validation is another technique used to examine the performance of a model, specifically to get an unbiased estimate of the model's performance on an independent dataset. The most common form of cross-validation is k-fold cross-validation, where the data is divided into k folds. It sidesteps the overfitting problem by training the model on some folds and then testing it on the remaining. An example of how k-fold cross-validation can be implemented using a mix of Python and EvaDB queries is shown below. 

--

A way to improve model performance is ensuring the data it is trained on is high-quality. Data preprocessing can remove undesired features from a dataset and go a long way in improving a model's generalization to independent data. For example, models are extremely sensitive to outliers in the training data by distorting the learned patterns and making the model harder to generalize. It is therefore in the user's best interest to remove outliers before the model training. One method to remove outliers is the IQR method, and an example of how it can be implemented on the House Rent data is shown below. 

--


