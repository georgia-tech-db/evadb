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
from mock import patch
from src.executor.create_udf_executor import CreateUDFExecutor


class CreateUdfExecutorTest(unittest.TestCase):

    @patch('src.catalog.catalog_manager.CatalogManager')
    def test_should_create_udf(self, mock):
        plan = type("CreateUDFPlan",
                    (),
                    {'name': 'udf',
                     'if_not_exists': False,
                     'inputs': ['inp'],
                     'outputs': ['out'],
                     'impl_path': 'test.py',
                     'udf_type': 'classification'})
        create_udf_executor = CreateUDFExecutor(plan)
        mock.return_value.create_udf.assert_called_with('udf', 'test.py', 'classification', ['inp', 'out'])
