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
import os

import cv2
import pandas as pd

from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError
from eva.models.storage.batch import Batch
from eva.planner.open_plan import OpenPlan


class OpenExecutor(AbstractExecutor):
    def __init__(self, node: OpenPlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        data_path = str(self.node.path)

        # Check if path exists.
        if not os.path.exists(data_path):
            raise ExecutorError("Path {} does not exist.".format(data_path))

        try:
            data = cv2.imread(data_path)
            yield Batch(pd.DataFrame([{"id": 0, "data": data}]))
        except Exception as e:
            raise ExecutorError(str(e))
