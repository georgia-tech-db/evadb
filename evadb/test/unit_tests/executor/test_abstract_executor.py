# coding=utf-8
# Copyright 2018-2023 EvaDB
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
from inspect import signature
from test.util import get_all_subclasses

from evadb.executor.abstract_executor import AbstractExecutor


class AbstractExecutorTest(unittest.TestCase):
    def test_constructor_args(self):
        derived_executor_classes = list(get_all_subclasses(AbstractExecutor))
        for derived_executor_class in derived_executor_classes:
            sig = signature(derived_executor_class.__init__)
            params = sig.parameters
            self.assertTrue(len(params) < 10)
