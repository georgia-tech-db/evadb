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

from mock import MagicMock

from eva.optimizer.cost_model import CostModel
from eva.optimizer.optimizer_context import OptimizerContext


class TestOptimizerContext(unittest.TestCase):
    def test_add_root(self):
        fake_opr = MagicMock()
        fake_opr.children = []

        opt_ctxt = OptimizerContext(CostModel())
        opt_ctxt.add_opr_to_group(fake_opr)
        self.assertEqual(len(opt_ctxt.memo.group_exprs), 1)
