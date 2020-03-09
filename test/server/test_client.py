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

import io

from src.server.client import start_client, start_multiple_clients

from src.utils.logging_manager import Logger

class ClientTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def test_single_client(self):
 
        host = "localhost"
        port = 5432
        
        #monkeypatch.setattr('sys.stdin', io.StringIO('foo\nfah\nexit'))
        
        try:
            start_client(host = host, 
                         port = port)
        
        except Exception as e:
            Logger().exception(e)

    def test_multiple_clients(self):
 
        client_count = 10
        host = "localhost"
        port = 5432
        
        try:
            start_multiple_clients(client_count= client_count, 
                                   host = host, 
                                   port = port)
        
        except Exception as e:
            Logger().exception(e)

    
if __name__ == '__main__':
    unittest.main()
