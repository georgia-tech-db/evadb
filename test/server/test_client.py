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
import time

import asyncio
import threading

from src.server.client import start_clients


class ClientTests(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.stop_clients_future = self.loop.create_future()
        asyncio.set_event_loop(None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_clients(self):

        host = "0.0.0.0"
        port = 5438
        client_count = 3

        def timeout_server():
            # need a more robust mechanism for when to cancel the future
            time.sleep(2)
            self.stop_clients_future.cancel()

        thread = threading.Thread(target=timeout_server)
        thread.daemon = True
        thread.start()

        summary = start_clients(client_count=client_count,
                                host=host,
                                port=port,
                                loop=self.loop,
                                stop_clients_future=self.stop_clients_future)

        self.assertEqual(summary[0], client_count)

        # none of the connections will work due to server not running
        exception_count = client_count
        self.assertEqual(summary[1], exception_count)


if __name__ == '__main__':
    unittest.main()
