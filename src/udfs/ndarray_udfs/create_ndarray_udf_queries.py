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

DummyObjectDetector_udf_query = """CREATE UDF DummyObjectDetector
                  INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                  OUTPUT (label NDARRAY STR(10))
                  TYPE  Classification
                  IMPL  'test/util.py';
        """


ArrayCount_udf_query = """CREATE UDF Array_Count
                    INPUT(frame_data NDARRAY UINT8(3, 256, 256), label TEXT(10)) 
                    OUTPUT(count INTEGER)
                    TYPE Ndarray
                    IMPL "src/udfs/ndarray_udfs/array_count.py";
        """
