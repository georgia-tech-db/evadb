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
import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.executor.abstract_executor import AbstractExecutor
from eva.models.storage.batch import Batch
from eva.parser.types import ShowType
from eva.planner.show_info_plan import ShowInfoPlan


class ShowInfoExecutor(AbstractExecutor):
    def __init__(self, node: ShowInfoPlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self):
        """Create udf executor

        Calls the catalog to create udf metadata.
        """
        catalog_manager = CatalogManager()
        show_entries = []
        if self.node.show_type is ShowType.UDFS:
            udfs = catalog_manager.get_all_udf_entries()
            for udf in udfs:
                show_entries.append(udf.display_format())

        yield Batch(pd.DataFrame(show_entries))
