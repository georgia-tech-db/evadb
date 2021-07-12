# coding=utf-8
# Copyright 2018-2020 EVA
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

# this file is to list out all the ndarray udf create queries in one place
# as constants

from src.server.command_handler import execute_query_fetch_all


DummyObjectDetector_udf_query = """CREATE UDF DummyObjectDetector
                  INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                  OUTPUT (label NDARRAY STR(10))
                  TYPE  Classification
                  IMPL  'test/util.py';
        """

DummyMultiObjectDetector_udf_query = """CREATE UDF DummyMultiObjectDetector
                  INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                  OUTPUT (labels NDARRAY STR(10))
                  TYPE  Classification
                  IMPL  'test/util.py';
        """

ArrayCount_udf_query = """CREATE UDF Array_Count
            INPUT(frame_data NDARRAY UINT8(3, 256, 256), label TEXT(10))
            OUTPUT(count INTEGER)
            TYPE Ndarray
            IMPL "src/udfs/ndarray_udfs/array_count.py";
        """
Unnest_udf_query = """CREATE UDF Unnest
                INPUT  (inp NDARRAY UINT8(10, 10, 10))
                OUTPUT (out NDARRAY UINT8(10, 10, 10))
                TYPE  Ndarray
                IMPL  "src/udfs/ndarray_udfs/unnest.py";
        """

Fastrcnn_udf_query = """CREATE UDF FastRCNNObjectDetector
      INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
      OUTPUT (labels NDARRAY STR(10), bboxes NDARRAY FLOAT32(10),
                scores NDARRAY FLOAT32(10))
      TYPE  Classification
      IMPL  'src/udfs/fastrcnn_object_detector.py';
      """


def init_builtin_udfs(mode='debug'):
    """
    Loads the builtin udfs into the system.
    This should be called when the system bootstraps.
    In debug mode, it also loads udfs used in the test suite.
    Arguments:
        mode (str): 'debug' or 'release'
    """
    queries = [Fastrcnn_udf_query, Unnest_udf_query, ArrayCount_udf_query]
    if mode == 'debug':
        queries.extend([DummyObjectDetector_udf_query,
                        DummyMultiObjectDetector_udf_query])

    for query in queries:
        execute_query_fetch_all(query)
