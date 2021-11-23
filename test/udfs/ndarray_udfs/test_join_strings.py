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
import unittest
from src.udfs.ndarray_udfs.join_strings import Join_Strings

class JoinTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_join_operation(self):

        inp = { "words":
                [["I","am","a", "girl"],
                ["Bag", "of", "words"],
                ["House", "of", "cards"]]
              }
        delimiter = " "
        concatenated_result = Join_Strings().exec(inp["words"], delimiter)

        expected_result = [
                        ["I am a girl"],
                        ["Bag of words"],
                        ["House of cards"]
                    ]
        print(concatenated_result)
        if expected_result == concatenated_result:
            print("Lists are equal")

if __name__ == '__main__':
    JoinTests().test_join_operation()