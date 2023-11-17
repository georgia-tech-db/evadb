Unit Testing UDFs in EvaDB
===========================

Introduction
------------

Unit testing is a crucial aspect of software development. When working with User Defined Functions (UDFs) in EvaDB, it's essential to ensure that they work correctly. This guide will walk you through the process of writing unit tests for UDFs and using mocking to simulate external dependencies.

Setting Up Test Environment
---------------------------

Before writing tests, set up a test environment. This often involves creating a test database or table and populating it with sample data.

.. code-block:: python

   def setUp(self) -> None:
       self.evadb = get_evadb_for_testing()
       self.evadb.catalog().reset()
       create_table_query = """CREATE TABLE IF NOT EXISTS TestTable (
            prompt TEXT(100));
       """
       execute_query_fetch_all(self.evadb, create_table_query)
       test_prompts = ["sample prompt"]
       for prompt in test_prompts:
           insert_query = f"""INSERT INTO TestTable (prompt) VALUES ('{prompt}')"""
           execute_query_fetch_all(self.evadb, insert_query)

Mocking External Dependencies
-----------------------------

When testing UDFs that rely on external services or APIs, use mocking to simulate these dependencies.

.. code-block:: python

   @patch("requests.get")
   @patch("external_library.Method", return_value={"data": [{"url": "mocked_url"}]})
   def test_udf(self, mock_method, mock_requests_get):
       # Mock the response from the external service
       mock_response = MagicMock()
       mock_response.content = "mocked content"
       mock_requests_get.return_value = mock_response

       # Rest of the test code...

Writing the Test
----------------

After setting up the environment and mocking dependencies, write the test for the UDF.

.. code-block:: python

   function_name = "ImageDownloadUDF"
   query = f"SELECT {function_name}(prompt) FROM TestTable;"
   output = execute_query_fetch_all(self.evadb, query)
   expected_output = [...]  # Expected output
   self.assertEqual(output, expected_output)

Cleaning Up After Tests
-----------------------

Clean up any resources used during testing, such as database tables.

.. code-block:: python

   def tearDown(self) -> None:
       execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS TestTable;")

Running the Tests
-----------------

Run the tests using a test runner like `unittest`.

.. code-block:: bash

   python -m unittest path_to_your_test_module.py

Conclusion
----------

Unit testing UDFs in EvaDB ensures their correctness and robustness. Mocking allows for simulating external dependencies, making tests faster and more deterministic.
