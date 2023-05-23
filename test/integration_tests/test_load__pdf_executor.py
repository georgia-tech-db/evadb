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
import glob
import multiprocessing as mp
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from test.util import (
    create_dummy_batches,
    create_dummy_csv_batches,
    create_large_scale_image_dataset,
    create_sample_csv,
    create_sample_video,
    file_remove,
    shutdown_ray,
)

import numpy as np
import pandas as pd
import pytest

from eva.binder.binder_utils import BinderError
from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.constants import EVA_ROOT_DIR
from eva.executor.executor_utils import ExecutorError
from eva.models.storage.batch import Batch
from eva.parser.types import FileFormatType
from eva.server.command_handler import execute_query_fetch_all


@pytest.mark.notparallel
class LoadExecutorTest(unittest.TestCase):
    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()

    def tearDown(self):
        shutdown_ray()

        execute_query_fetch_all("DROP TABLE IF EXISTS pdfs;")

    def test_load_pdfs(self):
        execute_query_fetch_all(
            f"""LOAD PDF '{EVA_ROOT_DIR}/data/documents/pdf_sample1.pdf' INTO pdfs;"""
        )
        result = execute_query_fetch_all("SELECT * from pdfs;")
        self.assertEqual(len(result.columns), 3)
        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main()
