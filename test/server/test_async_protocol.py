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

from src.server.async_protocol import EvaProtocolBuffer


class AsyncProtocolTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_empty_buffer(self):
        buf = EvaProtocolBuffer()
        buf.empty()
        self.assertEqual('', buf.buf)
        self.assertEqual(-1, buf.expected_length)

    def test_feed_data(self):
        buf = EvaProtocolBuffer()
        data1 = '4|12'
        data2 = '34'

        buf.feed_data(data1)
        self.assertEqual('12', buf.buf)
        self.assertEqual(4, buf.expected_length)

        buf.feed_data(data2)
        self.assertEqual('1234', buf.buf)
        self.assertEqual(4, buf.expected_length)

    def test_has_complete_message(self):
        buf = EvaProtocolBuffer()
        data1 = '4|12'
        data2 = '34'

        buf.feed_data(data1)
        self.assertFalse(buf.has_complete_message())
        buf.feed_data(data2)
        self.assertTrue(buf.has_complete_message())

    def test_read_message_one(self):
        buf = EvaProtocolBuffer()
        data1 = '4|12'
        data2 = '34'
        buf.feed_data(data1)
        buf.feed_data(data2)

        self.assertEqual('1234', buf.read_message())
        self.assertEqual('', buf.buf)
        self.assertEqual(-1, buf.expected_length)

    def test_read_message_two(self):
        buf = EvaProtocolBuffer()
        data1 = '4|123'
        data2 = '42|56'
        buf.feed_data(data1)
        buf.feed_data(data2)

        self.assertEqual('1234', buf.read_message())
        self.assertEqual('56', buf.read_message())
        self.assertEqual('', buf.buf)
        self.assertEqual(-1, buf.expected_length)

