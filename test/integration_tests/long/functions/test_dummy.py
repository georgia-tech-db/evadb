import unittest

import pandas as pd
from evadb.server.command_handler import execute_query_fetch_all
from evadb.configuration.constants import EvaDB_DATABASE_DIR, EvaDB_ROOT_DIR
from test.util import (
    get_evadb_for_testing,
    shutdown_ray,
    load_functions_for_testing
)

compas_dataset = '/home/jeff/evadb/data/divexplorer/compas_discretized.csv'

class DummyTest(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        self.evadb.catalog().reset()
        execute_query_fetch_all(self.evadb, "DROP FUNCTION IF EXISTS Dummy;")
        print('Dropped')
        load_functions_for_testing(self.evadb, mode='debug')

    def tearDown(self):
        shutdown_ray()
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS test_csv;")
        print('Dropped function')
        execute_query_fetch_all(self.evadb, "DROP FUNCTION IF EXISTS Dummy;")

    # def test_show(self):
    #     # show_query = "SHOW FUNCTIONS;"
    #     # show_query = "SHOW FUNCTIONS;"
    #     show_query = "SHOW FUNCTIONS_ALL;"
    #     result = execute_query_fetch_all(self.evadb, show_query)
    #     # print(result.columns)
    #     # print(type(result))
    #     # print(result.frames[['name', 'inputs', 'outputs']])
    #     # print(result.frames)
    #     print(result)
    #     print(result.frames)


    def test_dummy_function(self):
        import time

        create_table_query = """
            CREATE TABLE IF NOT EXISTS test_csv(
                age INTEGER,
                charge TEXT(30),
                race TEXT(30),
                sex TEXT(10),
                n_prior TEXT(30),
                stay TEXT(10),
                class INTEGER,
                predicted INTEGER
            );
        """
        load_query = f"LOAD CSV '{compas_dataset}' INTO test_csv;"

        execute_query_fetch_all(self.evadb, create_table_query)
        execute_query_fetch_all(self.evadb, load_query)
        # print(execute_query_fetch_all(self.evadb, "SELECT * FROM MyCompas LIMIT 10;"))

        create_fn_query = (
            f"""CREATE FUNCTION IF NOT EXISTS Dummy 
                IMPL  '{EvaDB_ROOT_DIR}/evadb/functions/dummy.py';"""
        )
        execute_query_fetch_all(self.evadb, create_fn_query)

        t = time.time()
        # SELECT Dummy(age, charge, race, sex, n_prior, stay, class, predicted) from test_csv;
        print(execute_query_fetch_all(self.evadb, "SELECT * FROM test_csv;"))
        select_query = """
        SELECT Dummy(*) from test_csv;
        """
        result = execute_query_fetch_all(self.evadb, select_query)
        print(result)
        print('overall time', time.time() - t)