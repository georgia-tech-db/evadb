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
import logging

import faiss
import numpy as np
import os
import pandas as pd

from eva.executor.abstract_executor import AbstractExecutor
from eva.planner.select_like_plan import SelectLikePlan
from eva.catalog.catalog_manager import CatalogManager


class SelectLikeExecutor(AbstractExecutor):
    def __init__(self, node: SelectLikePlan):
        super().__init__(node)
        self.table_name = node.table_ref.table.table_name
        self.target_img = node.target_img
        self.catalog_manager = CatalogManager()

    def validate(self):
        pass

    def exec(self):
        # TODO
        logging.info("select like executor reached")
