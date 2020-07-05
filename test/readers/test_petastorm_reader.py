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
from unittest.mock import patch
import numpy as np

from src.readers.petastorm_reader import PetastormReader


class PetastormLoaderTest(unittest.TestCase):

    class DummyReader:
        def __init__(self, data):
            self.data = data

        def __enter__(self):
            return self

        def __iter__(self):
            return self.data

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    @patch("src.readers.petastorm_reader.make_reader")
    def test_should_call_petastorm_make_reader_with_correct_params(self,
                                                                   mock):
        petastorm_reader = PetastormReader(file_url='dummy.avi', cur_shard=2,
                                           shard_count=3)
        print(list(petastorm_reader._read()))
        mock.assert_called_once_with('dummy.avi', shard_count=3, cur_shard=2)

    @patch("src.readers.petastorm_reader.make_reader")
    def test_should_read_data_using_petastorm_reader(self, mock):
        petastorm_reader = PetastormReader(file_url='dummy.avi')
        dummy_values = map(lambda i: np.ones((2, 2, 3)) * i, range(3))
        mock.return_value = self.DummyReader(dummy_values)
        actual = list(petastorm_reader._read())
        expected = list(dummy_values)
        self.assertTrue(all([np.allclose(i, j)
                             for i, j in zip(actual, expected)]))
