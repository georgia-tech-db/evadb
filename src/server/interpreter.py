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

from cmd import Cmd


class EvaCommandInterpreter(Cmd):

    # Store results from server
    _server_result = None
    _url = None

    def __init__(self):
        super().__init__()

    def set_protocol(self, protocol):
        self._protocol = protocol

    def do_greet(self, line):
        print("greeting")

    def emptyline(self):
        print("Enter a valid query.")
        return False

    def onecmd(self, s):
        if s == "":
            return self.emptyline()
        elif (s == "exit" or s == "EXIT"):
            return SystemExit
        else:
            return self.do_query(s)

    def do_query(self, query):
        """Takes in SQL query and generates the output"""

        self._protocol._response_chunk = None
        self._protocol.send_message(query)
        while self._protocol._response_chunk is None:
            _ = 1
        self._server_result = self._protocol._response_chunk
        print(self._server_result)
        return False

    def do_quit(self, args):
        """Quits the program."""
        return True

    def do_exit(self, args):
        """Quits the program."""
        return True

    def do_EOF(self, line):
        return True
