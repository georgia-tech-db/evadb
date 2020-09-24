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

from src.models.storage.batch import Batch
from src.models.server.response import ResponseStatus, Response
from test.util import create_dataframe


class ResponseTest(unittest.TestCase):

    def test_server_response_to_json_string(self):
        batch = Batch(frames=create_dataframe())
        response = Response(status=ResponseStatus.SUCCESS,
                            batch=batch)
        print(response.to_json())

    def test_server_reponse_from_json_string(self):
        batch = Batch(frames=create_dataframe())
        response = Response(status=ResponseStatus.SUCCESS,
                            batch=batch)
        response2 = Response.from_json(response.to_json())
        self.assertEqual(response, response2)




