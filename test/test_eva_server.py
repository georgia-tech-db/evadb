# coding=utf-8
# Copyright 2018-2022 EVA
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

from mock import MagicMock, patch

from eva.eva_server import eva, main


class EVAServerTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @patch("eva.eva_server.init_builtin_udfs")
    @patch("eva.eva_server.eva")
    @patch("eva.eva_server.ConfigurationManager")
    def test_main(self, mock_config, mock_eva, mock_udfs):
        mock_obj_1 = MagicMock()
        mock_config.return_value.get_value = mock_obj_1
        main()
        mock_obj_1.assert_called_with("core", "mode")
        mock_udfs.assert_called_with(mode=mock_obj_1())
        mock_eva.assert_called_once()

    @patch("eva.eva_server.ConfigurationManager")
    @patch("asyncio.new_event_loop")
    @patch("asyncio.run")
    def test_eva(self, mock_run, mock_new_event_loop, mock_config):
        mock_obj_1 = MagicMock()
        mock_obj_2 = MagicMock()
        mock_config.return_value.get_value = mock_obj_1
        mock_new_event_loop.return_value.create_future = mock_obj_2
        eva()
        self.assertEqual(mock_obj_1.call_count, 3)
        mock_new_event_loop.assert_called_once()
        mock_obj_2.assert_called_once()
        mock_run.assert_called_once()
