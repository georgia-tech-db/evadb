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
from src.models.server.response import Response


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

        self._protocol._response_chunks = []
        self._protocol.send_message(query)
        while len(self._protocol._response_chunks) == 0:
            _ = 1
        segs = self._protocol._response_chunks[0].split('|', 1)
        result_length = int(segs[0])
        self._server_result = segs[1]
        next_chunk = 1
        while len(self._server_result) < result_length:
            #print('Total length: %d, Received: %d' %
            #      (result_length, len(self._server_result)), end='\r')
            # next chunk is not avaiable yet
            while len(self._protocol._response_chunks) <= next_chunk:
                _ = 1
            self._server_result += self._protocol._response_chunks[next_chunk]
            next_chunk += 1

        #print('Total length: %d, Received: %d' %
        #      (result_length, len(self._server_result)))
        response = Response.from_json(self._server_result)
        print(response)
        return False

    def do_quit(self, args):
        """Quits the program."""
        return True

    def do_exit(self, args):
        """Quits the program."""
        return True

    def do_EOF(self, line):
        return True
