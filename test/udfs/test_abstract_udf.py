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
import inspect
import unittest
from enum import Enum
from inspect import isabstract
from test.util import get_all_subclasses, get_mock_object

import eva
from eva.udfs.abstract.abstract_udf import AbstractUDF


class AbstractUDFTest(unittest.TestCase):
    def test_udf_abstract_functions(self):
        derived_udf_classes = list(get_all_subclasses(AbstractUDF))
        for derived_udf_class in derived_udf_classes:
            if isabstract(derived_udf_class) is False:
                obj = derived_udf_class()
                name = obj.name
                self.assertTrue(name is not None)

    def test_all_classes(self):
        def get_all_classes(module, level):
            class_list = []

            if level == 4:
                return []

            for _, obj in inspect.getmembers(module):
                if inspect.ismodule(obj):
                    sublist = get_all_classes(obj, level + 1)
                    if sublist != []:
                        class_list.append(sublist)
                elif inspect.isclass(obj):
                    if inspect.isabstract(obj) is False:
                        if inspect.isbuiltin(obj) is False:
                            try:
                                source_file = inspect.getsourcefile(obj)
                                if source_file is None:
                                    continue
                                if issubclass(obj, Enum):
                                    continue
                                if "python" not in str(source_file):
                                    class_list.append([obj])
                            except OSError:
                                pass

            flat_class_list = [item for sublist in class_list for item in sublist]
            return set(flat_class_list)

        class_list = get_all_classes(eva, 1)

        base_id = 0
        ref_object = None
        for c in class_list:
            sig = inspect.signature(c.__init__)
            params = sig.parameters
            len_params = len(params)
            if "kwargs" in params:
                len_params = len_params - 1
            if "args" in params:
                len_params = len_params - 1
            try:
                dummy_object = get_mock_object(c, len_params)
                if base_id == 0:
                    ref_object = dummy_object
                else:
                    self.assertNotEqual(ref_object, dummy_object)
            except Exception:
                print(c)
                pass
