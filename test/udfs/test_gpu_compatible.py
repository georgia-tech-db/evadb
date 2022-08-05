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

from eva.udfs.gpu_compatible import GPUCompatible


class GPUCompatibleExample:
    def to_device(self, device: str) -> object:
        return self


class GPUCompatibleTest(unittest.TestCase):
    def test_is_member_of_protocol(self):
        gpu_compat = GPUCompatibleExample()
        assert isinstance(gpu_compat, GPUCompatible)
