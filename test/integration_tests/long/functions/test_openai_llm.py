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
import os
import unittest
from test.util import (
    file_remove,
    get_evadb_for_testing,
    get_logical_query_plan,
    get_physical_query_plan,
    load_functions_for_testing,
    shutdown_ray,
)

import pandas as pd
import pytest

from evadb.models.storage.batch import Batch
from evadb.optimizer.operators import LogicalLLM
from evadb.plan_nodes.llm_plan import LLMPlan
from evadb.server.command_handler import execute_query_fetch_all

NUM_FRAMES = 10

# set OPENAI_API_KEY
os.environ["OPENAI_API_KEY"] = "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"
os.environ["OPENAI_BUDGET"] = "10"

@pytest.mark.notparallel
class OpenAILLM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # add OpenAILLM to LLM_FUNCTIONS, CACHEABLE_FUNCTIONS
        from evadb.constants import CACHEABLE_FUNCTIONS, LLM_FUNCTIONS

        cls.function_name = "OpenAILLM"

        LLM_FUNCTIONS += [cls.function_name.lower()]
        CACHEABLE_FUNCTIONS += [cls.function_name.lower()]

        cls.evadb = get_evadb_for_testing()
        cls.evadb.catalog().reset()

        load_functions_for_testing(cls.evadb)
        execute_query_fetch_all(cls.evadb, "CREATE TABLE fruitTable (data TEXT(100))")
        cls.data_list = [
            "The color of apple is red",
            "The color of banana is yellow",
        ]
        for data in cls.data_list:
            execute_query_fetch_all(
                cls.evadb, f"INSERT INTO fruitTable (data) VALUES ('{data}')"
            )

        
        execute_query_fetch_all(cls.evadb, f"DROP FUNCTION IF EXISTS {cls.function_name};")

        create_function_query = f"""CREATE FUNCTION IF NOT EXISTS{cls.function_name}
            IMPL 'evadb/functions/llms/openai.py';
        """
        execute_query_fetch_all(cls.evadb, create_function_query)

    @classmethod
    def tearDownClass(cls):
        shutdown_ray()

        file_remove("dummy.avi")

    def test_openai_llm(self):
        prompt = '"What is the fruit described in this sentence"'
        select_query = f"SELECT {self.function_name}({prompt}, data) FROM fruitTable;"
        logical_plan = get_logical_query_plan(self.evadb, select_query)
        assert len(list(logical_plan.find_all(LogicalLLM))) > 0
        physical_plan = get_physical_query_plan(self.evadb, select_query)
        assert len(list(physical_plan.find_all(LLMPlan))) > 0
        batches = execute_query_fetch_all(self.evadb, select_query)
        self.assertEqual(batches.columns, [f"{self.function_name.lower()}.response"])

if __name__ == "__main__":
    unittest.main()
