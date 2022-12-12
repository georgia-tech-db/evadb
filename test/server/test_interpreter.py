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
import contextlib
import io
import unittest
from unittest.mock import MagicMock

from mock import patch

from eva.server.interpreter import EvaCommandInterpreter, start_cmd_client


class InterpreterTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_cmd_emptyline_should_return_false(self):
        prompt = EvaCommandInterpreter()
        prompt.prompt = "> "

        with io.StringIO() as buf:
            with contextlib.redirect_stdout(buf):
                self.assertFalse(prompt.emptyline())
                self.assertTrue("Enter a valid query" in buf.getvalue())

    def test_cmd_exit_should_return_true(self):
        prompt = EvaCommandInterpreter()

        self.assertEqual(SystemExit, prompt.do_quit(None))
        self.assertEqual(SystemExit, prompt.do_exit(None))

    @patch("eva.server.interpreter.EvaCommandInterpreter.emptyline")
    def test_onecmd_with_emptyline(self, mock_emptyline):
        prompt = EvaCommandInterpreter()
        mock_emptyline.return_value = False

        prompt.onecmd("")
        mock_emptyline.assert_called_once()

    def test_onecmd_with_exit(self):
        prompt = EvaCommandInterpreter()
        self.assertEqual(SystemExit, prompt.onecmd("exit"))
        self.assertEqual(SystemExit, prompt.onecmd("quit"))

    def test_onecmd_with_do_query(self):
        prompt = EvaCommandInterpreter()
        prompt.cursor = MagicMock()
        prompt.cursor.fetch_all.return_value = "123"

        query = "SELECT id FROM MyVIdeo"
        with io.StringIO() as buf:
            with contextlib.redirect_stdout(buf):
                self.assertFalse(prompt.onecmd(query))
                prompt.cursor.execute.assert_called_once_with(query)
                prompt.cursor.fetch_all.assert_called_once_with()
                self.assertTrue("123" in buf.getvalue())

    # We are mocking the connect funciton call that gets imported into
    # interpreter instead of the one in db_api.
    @patch("eva.server.interpreter.connect")
    @patch("eva.server.interpreter.EvaCommandInterpreter.cmdloop")
    def test_start_cmd_client(self, mock_cmdloop, mock_connect):
        class MOCKCONNECTION:
            def cursor(self):
                return None

        mock_connect.return_value = MOCKCONNECTION()

        host = "0.0.0.0"
        port = 5432
        start_cmd_client(host, port)

        mock_connect.assert_called_once_with(host, port)
        mock_cmdloop.assert_called_once()
