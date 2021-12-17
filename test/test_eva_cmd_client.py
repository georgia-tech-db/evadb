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
import mock
from eva.eva_cmd_client import main
from eva.eva_cmd_client import parse_args


class CMDClientTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @mock.patch('eva.eva_cmd_client.eva_client')
    def test_main(self, mock_client):
        main()
        mock_client.called_once_with('0.0.0.0', 5432)

    def test_parse_args(self):
        args = parse_args(['-P', '2345', '-H', 'test'])
        self.assertEqual(args.host, 'test')
        self.assertEqual(args.port, 2345)
