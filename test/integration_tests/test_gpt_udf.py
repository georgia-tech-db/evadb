import unittest

from eva.server.command_handler import execute_query_fetch_all
import os
from test.util import create_text_csv, file_remove

class GPTUDFsTest(unittest.TestCase):
    
    @unittest.skip("Skip as it requires api key")
    def test_gpt_udf(self):
        udf_name = "GPTUdf"
        
        response = execute_query_fetch_all(f"DROP UDF IF EXISTS {udf_name};")
    
        self.csv_file_path = "test/data/queries.csv"
        
        
        create_udf_query = f"""CREATE UDF {udf_name}
            IMPL 'eva/udfs/gpt_udf.py'
        """
        execute_query_fetch_all(create_udf_query)
        
        execute_query_fetch_all(f"DROP TABLE MyTextCSV;")
        create_table_query = """CREATE TABLE IF NOT EXISTS MyTextCSV (
                id INTEGER UNIQUE,
                query TEXT (100)
            );"""
        execute_query_fetch_all(create_table_query)
        
        csv_query = f"""LOAD CSV '{self.csv_file_path}' INTO MyTextCSV;"""
        execute_query_fetch_all(csv_query)
        
        gpt_query =f"SELECT {udf_name}(query) FROM MyTextCSV;"
        output_batch = execute_query_fetch_all(gpt_query)
        self.assertEqual(len(output_batch), 2)
        self.assertEqual(len(list(output_batch.columns)), 2)
        
    
if __name__ == "__main__":
    suite = unittest.TestSuite()
    my_test = GPTUDFsTest()
    suite.addTest(GPTUDFsTest("test_gpt_udf"))
    unittest.TextTestRunner().run(suite)
    