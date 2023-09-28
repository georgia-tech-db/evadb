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
from test.markers import stable_diffusion_skip_marker
from test.util import get_evadb_for_testing

import pandas as pd

from evadb.server.command_handler import execute_query_fetch_all

class StableDiffusionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.evadb = get_evadb_for_testing()
        self.evadb.catalog().reset()
        create_table_query = """CREATE TABLE IF NOT EXISTS ImageGen (
             prompt TEXT(100));
                """
        execute_query_fetch_all(self.evadb, create_table_query)

        test_prompts = ['pink cat riding a rocket to the moon']

        for prompt in test_prompts:
            insert_query = f"""INSERT INTO ImageGen (prompt) VALUES ('{prompt}')"""
            execute_query_fetch_all(self.evadb, insert_query)
    
    def tearDown(self) -> None:
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS ImageGen;")
    
    @stable_diffusion_skip_marker
    def test_stable_diffusion_image_generation(self):
        function_name = 'StableDiffusion'

        execute_query_fetch_all(self.evadb, f"DROP FUNCTION IF EXISTS {function_name};")

        create_function_query = f"""CREATE FUNCTION IF NOT EXISTS{function_name}
            IMPL 'evadb/functions/stable_diffusion.py';
        """
        execute_query_fetch_all(self.evadb, create_function_query)

        gpt_query = f"SELECT {function_name}(prompt) FROM ImageGen;"
        output_batch = execute_query_fetch_all(self.evadb, gpt_query)
        
        self.assertEqual(output_batch.columns, ["stablediffusion.response"])