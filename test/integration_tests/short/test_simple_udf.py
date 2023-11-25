import unittest
import os
import pandas as pd
import tempfile
from test.util import get_evadb_for_testing, shutdown_ray

from evadb.executor.executor_utils import ExecutorError
from evadb.server.command_handler import execute_query_fetch_all

class SimpleUDFTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        cls.evadb.catalog().reset()
    
    def setUp(self):
        fd, self.temp_path = tempfile.mkstemp(suffix=".py")
        # Create a python file with two functions
        with os.fdopen(fd, "w") as f:
            f.write("def mod5(id:int)->int:\n")
            f.write("\treturn id % 5\n")
            f.write("\n")
            f.write("def isEven(id:int)->bool:\n")
            f.write("\treturn id % 2 == 0\n")
        # Create a table with 10 rows
        execute_query_fetch_all(self.evadb, "CREATE TABLE IF NOT EXISTS test (id INTEGER);")
        for i in range(10):
            execute_query_fetch_all(self.evadb, f"INSERT INTO test (id) VALUES ({i});")     
    
    def tearDown(self):
        # Delete the python file
        os.remove(self.temp_path)
        # Delete the table
        execute_query_fetch_all(self.evadb, "DROP TABLE test;")

    def test_first_udf(self):
        # Create the UDF
        execute_query_fetch_all(self.evadb, f"CREATE FUNCTION mod5 IMPL '{self.temp_path}';")
        # Query the UDF
        result = execute_query_fetch_all(self.evadb, "SELECT mod5(id) FROM test;")
        expected = pd.DataFrame({"mod5.mod5": [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]})
        # Check the result
        self.assertTrue(result.frames.equals(expected))
        # Delete the UDF
        execute_query_fetch_all(self.evadb, "DROP FUNCTION mod5;")
    
    def test_second_udf(self):
        # Create the UDF
        execute_query_fetch_all(self.evadb, f"CREATE FUNCTION isEven IMPL '{self.temp_path}';")
        # Query the UDF
        result = execute_query_fetch_all(self.evadb, "SELECT isEven(id) FROM test;")
        expected = pd.DataFrame({"iseven.iseven": [i % 2 == 0 for i in range(10)]})
        # Check the result
        self.assertEqual(result.frames.equals(expected), True)
        # Delete the UDF
        execute_query_fetch_all(self.evadb, "DROP FUNCTION isEven;")