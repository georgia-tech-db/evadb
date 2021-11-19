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
import os
import numpy as np

from src.eva.readers.petastorm_reader import PetastormReader
from src.eva.configuration.configuration_manager import ConfigurationManager

from test.util import PATH_PREFIX


class PetastormLoaderTest(unittest.TestCase):

    class DummyRow:
        def __init__(self, frame_id, frame_data):
            self.frame_id = frame_id
            self.frame_data = frame_data

        def _asdict(self):
            return {'id': self.frame_id, 'data': self.frame_data}

    class DummyReader:
        def __init__(self, data):
            self.data = data

        def __enter__(self):
            return self

        def __iter__(self):
            return self.data

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    @patch("eva.readers.petastorm_reader.make_reader")
    def test_should_call_petastorm_make_reader_with_correct_params(self,
                                                                   mock):
        petastorm_reader = PetastormReader(
            file_url=os.path.join(PATH_PREFIX, 'dummy.avi'),
            batch_mem_size=3000,
            cur_shard=2,
            shard_count=3,
            predicate='pred')
        list(petastorm_reader._read())
        mock.assert_called_once_with(
            os.path.join(PATH_PREFIX, 'dummy.avi'),
            shard_count=3,
            cur_shard=2,
            predicate='pred',
            cache_type=None,
            cache_location=None,
            cache_size_limit=None,
            cache_row_size_estimate=None)

    @patch("eva.readers.petastorm_reader.make_reader")
    def test_should_call_petastorm_make_reader_with_negative_shards(self,
                                                                    mock):
        petastorm_reader = PetastormReader(
            file_url=os.path.join(PATH_PREFIX, 'dummy.avi'),
            batch_mem_size=3000,
            cur_shard=-1,
            shard_count=-2)
        list(petastorm_reader._read())
        petastorm_config = ConfigurationManager().get_value('storage',
                                                            'petastorm')
        mock.assert_called_once_with(
            os.path.join(PATH_PREFIX, 'dummy.avi'),
            shard_count=None,
            cur_shard=None,
            predicate=None,
            cache_location=petastorm_config.get('cache_location', None),
            cache_row_size_estimate=petastorm_config.get(
                'cache_row_size_estimate', None),
            cache_size_limit=petastorm_config.get('cache_size_limit', None),
            cache_type=petastorm_config.get('cache_type', None))

    @patch("eva.readers.petastorm_reader.make_reader")
    def test_should_read_data_using_petastorm_reader(self, mock):
        petastorm_reader = PetastormReader(
            file_url=os.path.join(PATH_PREFIX, 'dummy.avi'),
            batch_mem_size=3000)
        dummy_values = map(lambda i: self.DummyRow(
            i, np.ones((2, 2, 3)) * i), range(3))
        mock.return_value = self.DummyReader(dummy_values)
        actual = list(petastorm_reader._read())
        expected = list(dummy_values)
        self.assertTrue(all([np.allclose(i, j)
                             for i, j in zip(actual, expected)]))
