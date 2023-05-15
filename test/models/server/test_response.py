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
from test.util import create_dataframe

from eva.models.server.response import Response, ResponseStatus
from eva.models.storage.batch import Batch


class ResponseTest(unittest.TestCase):
    def test_server_response_serialize_deserialize(self):
        batch = Batch(frames=create_dataframe())
        response = Response(status=ResponseStatus.SUCCESS, batch=batch)
        response2 = Response.deserialize(response.serialize())
        print(response2)
        self.assertEqual(response, response2)
