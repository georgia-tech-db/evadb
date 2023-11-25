import pytest
import evadb
import evadb
import shutil
import cv2
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from test.util import create_text_csv, file_remove, get_evadb_for_testing
from evadb.executor.executor_utils import ExecutorError
from evadb.server.command_handler import execute_query_fetch_all
import random
import string
from datetime import datetime, timedelta
from evadb.catalog.catalog_type import NdArrayType

def test_image_processing():

    file_path = os.path.join("/Users/yiningyuan/Desktop/evadb/evadb/test/integration_tests/long/functions/ndarray")
    con = get_evadb_for_testing()

    execute_query_fetch_all(con, "DROP TABLE IF EXISTS Image;")
    execute_query_fetch_all(con, "LOAD IMAGE '/Users/yiningyuan/Desktop/evadb/evadb/data/images/*.jpeg' INTO Image")

    execute_query_fetch_all(con, "DROP FUNCTION IF EXISTS grayscale;")
    execute_query_fetch_all(con, f"CREATE FUNCTION grayscale IMPL  '{file_path}/grayscale.py';")

    execute_query_fetch_all(con, "DROP FUNCTION IF EXISTS highpass;")
    execute_query_fetch_all(con, f"CREATE FUNCTION highpass IMPL  '{file_path}/high_pass.py';")

    execute_query_fetch_all(con, "DROP FUNCTION IF EXISTS blob_detector;")
    execute_query_fetch_all(con, f"CREATE FUNCTION blob_detector IMPL  '{file_path}/blob_detector.py';")

    execute_query_fetch_all(con, "DROP FUNCTION IF EXISTS threshold;")
    execute_query_fetch_all(con, f"CREATE FUNCTION threshold IMPL  '{file_path}/threshold.py';")

    # Call the functionality you want to test
    res = execute_query_fetch_all(con, """
        SELECT img.data, blob_detector(thresh.data)
        FROM Image as img
        JOIN LATERAL grayscale(img.data) AS gray(data)
        JOIN LATERAL highpass(gray.data) AS high(data)
        JOIN LATERAL threshold(high.data) AS thresh(data)
        """)
    print("----------------------------------------------------")
    # Assert expected outcomes
    assert len(res) > 0  # Example assertion
    print(res)
    res1 = execute_query_fetch_all(con, """
        SELECT img.data, blob_detector(threshold(highpass(grayscale(img.data))))
        FROM Image as img""")

    assert res==res1
    print("NAIVE TEST PASSED!")
if __name__ == "__main__":
    test_image_processing()