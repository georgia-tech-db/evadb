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

.. code-block:: python

   import pandas as pd

   k = 5 # 5 folds will be used in this example 
   cursor.query("""
      USE postgres_data {
         CREATE TABLE IF NOT EXISTS dataset_indices AS
         SELECT customer_id, NTILE(5) OVER (ORDER BY customer_id) AS fold
         FROM bank_predictor
      }""").df() # assigns a fold number 1-5 for each data point
   mse_scores = []
   for i in range(1,k):
      # makes a table of the training set which includes all folds except the current fold 
      first_query = """
         USE postgres_data {
            CREATE TABLE IF NOT EXISTS training_set AS
            SELECT * FROM bank_predictor
            WHERE customer_id NOT IN (SELECT customer_id FROM dataset_indices WHERE fold = """
            + str(i) + """)}""" 
      # makes a table of the testing set which is the current fold 
      second_query = """
         USE postgres_data {
            CREATE TABLE IF NOT EXISTS testing_set AS
            SELECT * FROM bank_predictor
            WHERE customer_id IN (SELECT customer_id FROM dataset_indices WHERE fold = """ 
            + str(i) + """)}"""
      cursor.query(first_query).df()
      cursor.query(second_query).df()

      # trains the model on the training set 
      cursor.query("""CREATE OR REPLACE FUNCTION BankPredictor FROM
          ( SELECT * FROM postgres_data.training_set )
          TYPE Ludwig
          PREDICT 'churn'
          TIME_LIMIT 3600;""").df()

      # uses the model to predict the testing set values 
      predictions = cursor.query("""
        SELECT customer_id, churn, predicted_churn
        FROM postgres_data.testing_set
        JOIN LATERAL BankPredictor(*) AS Predicted(predicted_churn)""").df()

      # finds the mean squared error between the expected and predicted values and appends to list 
      mse = (predictions['churn'] - predictions['predicted_churn'])**2
      mse_scores.append(mse.mean())

      cursor.query("""
        USE postgres_data {
           DROP TABLE IF EXISTS training_set}""").df()

     cursor.query("""
        USE postgres_data {
           DROP TABLE IF EXISTS testing_set}""").df()

   # finds the overall mean of all mean squared error
   # this value allows the user to judge how accurate the model is on independent data 
   final_mean = sum(mse_scores)/len(mse_scores)


A way to improve model performance is ensuring the data it is trained on is high-quality. Data preprocessing can remove undesired features from a dataset and go a long way in improving a model's generalization to independent data. For example, models are extremely sensitive to outliers in the training data by distorting the learned patterns and making the model harder to generalize. It is therefore in the user's best interest to remove outliers before the model training. One method to remove outliers is the IQR method, and an example of how it can be implemented on the House Rent data is shown below. 

--


