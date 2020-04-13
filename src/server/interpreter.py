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

import random
import glob

from PIL import Image
from cmd import Cmd

class EvaCommandInterpreter(Cmd):

    # Store results from server
    _server_result = None
    url = None

    def __init__(self):
        super().__init__()

        # Create table on connecting to server

    def set_protocol(self, protocol):
        self.protocol = protocol

    def do_greet(self, line):
        print("greeting")
    
    def emptyline(self):
        print ("Enter a valid query.")
        return False
    
    def onecmd(self, s):

        # Send request to server
        if s=="":
            return self.emptyline()
        elif(s == "exit" or s == "EXIT"):
            raise SystemExit
        else:
            return self.do_query(s)
    

    def do_query(self, query):
        """Takes in SQL query and generates the output"""

        # Type exit to stop program
        
        self.protocol.send_message(query)
        while self.protocol._response_chunk == None:
                _ = 1
            
        _server_result = self.protocol._response_chunk
        self.protocol._response_chunk = None


    def do_quit(self, args):
        """Quits the program."""
        # raise SystemExit
        return True

    def do_exit(self, args):
        """Quits the program."""
        # raise SystemExit
        return True

    def do_EOF(self, line):
        return True
