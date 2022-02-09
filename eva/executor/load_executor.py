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

import os
import pandas as pd

from eva.configuration.configuration_manager import ConfigurationManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.load_meta_executor import LoadMetaExecutor
from eva.executor.load_video_executor import LoadVideoExecutor
from eva.planner.load_data_plan import LoadDataPlan

class LoadDataExecutor(AbstractExecutor):

    def __init__(self, node: LoadDataPlan):
        super().__init__(node)
        config = ConfigurationManager()
        self.path_prefix = config.get_value('storage', 'path_prefix')

    def validate(self):
        pass

    def exec(self):
        """
        Use TYPE to determine the type of data to load. 
        """
        
        print(f"AbstractLoadDataExecutor: inside exec")

        # TODO: Currently using file extension to decide which executor to invoke. Figure out how to get TYPE from the query
        video_exts = ['.mp4']
        meta_exts = ['.csv']
        file_ext = os.path.splitext(self.node.file_path)[1]

        # invoke the appropriate executor
        if file_ext in meta_exts:
            executor = LoadMetaExecutor(self.node)
        elif file_ext in video_exts:
            executor = LoadVideoExecutor(self.node)

        # for each batch, exec the executor
        for batch in executor.exec():
            yield batch


