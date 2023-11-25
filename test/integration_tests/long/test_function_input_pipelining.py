# coding=utf-8
# Copyright 2018-2023 EvaDB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from test.util import get_evadb_for_testing

from evadb.server.command_handler import execute_query_fetch_all


def test_image_processing():
    file_path = os.path.join(
        "/Users/yiningyuan/Desktop/evadb/evadb/test/integration_tests/long/functions/ndarray"
    )
    con = get_evadb_for_testing()

    execute_query_fetch_all(con, "DROP TABLE IF EXISTS Image;")
    execute_query_fetch_all(
        con,
        "LOAD IMAGE '/Users/yiningyuan/Desktop/evadb/evadb/data/images/*.jpeg' INTO Image",
    )

    execute_query_fetch_all(con, "DROP FUNCTION IF EXISTS grayscale;")
    execute_query_fetch_all(
        con, f"CREATE FUNCTION grayscale IMPL  '{file_path}/grayscale.py';"
    )

    execute_query_fetch_all(con, "DROP FUNCTION IF EXISTS highpass;")
    execute_query_fetch_all(
        con, f"CREATE FUNCTION highpass IMPL  '{file_path}/high_pass.py';"
    )

    execute_query_fetch_all(con, "DROP FUNCTION IF EXISTS blob_detector;")
    execute_query_fetch_all(
        con, f"CREATE FUNCTION blob_detector IMPL  '{file_path}/blob_detector.py';"
    )

    execute_query_fetch_all(con, "DROP FUNCTION IF EXISTS threshold;")
    execute_query_fetch_all(
        con, f"CREATE FUNCTION threshold IMPL  '{file_path}/threshold.py';"
    )

    # Call the functionality you want to test
    res = execute_query_fetch_all(
        con,
        """
        SELECT img.data, blob_detector(thresh.data)
        FROM Image as img
        JOIN LATERAL grayscale(img.data) AS gray(data)
        JOIN LATERAL highpass(gray.data) AS high(data)
        JOIN LATERAL threshold(high.data) AS thresh(data)
        """,
    )
    # Assert expected outcomes
    assert len(res) > 0  # Example assertion
    res1 = execute_query_fetch_all(
        con,
        """
        SELECT img.data, blob_detector(threshold(highpass(grayscale(img.data))))
        FROM Image as img""",
    )

    assert res == res1


if __name__ == "__main__":
    test_image_processing()
