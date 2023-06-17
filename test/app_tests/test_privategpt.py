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
import shutil
import subprocess
import unittest
from pathlib import Path
from test.util import get_evadb_for_testing, shutdown_ray

import pytest
import requests


@pytest.mark.notparallel
class PrivateGPTTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        cls.evadb.catalog().reset()
        os.environ["ray"] = str(cls.evadb.config.get_value("experimental", "ray"))

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self) -> None:
        shutdown_ray()

        source_directory = "source_documents"
        if shutil.os.path.exists(source_directory):
            shutil.rmtree(source_directory)

    @unittest.skip("disable test due to inference time")
    def test_should_run_privategpt(self):
        ##################
        # INGEST
        ##################
        print("INGEST")

        source_directory = "source_documents"
        if shutil.os.path.exists(source_directory):
            shutil.rmtree(source_directory)

        url = "https://www.eisenhowerlibrary.gov/sites/default/files/file/1953_state_of_the_union.pdf"
        pdf_destination = "state_of_the_union.pdf"
        response = requests.get(url)
        if response.status_code == 200:
            with open(pdf_destination, "wb") as file:
                file.write(response.content)

        os.makedirs(source_directory, exist_ok=True)
        shutil.move(pdf_destination, source_directory)

        app_path = Path("apps", "privategpt", "ingest.py")
        inputs = ""
        command = ["python", app_path, "--directory", "source_documents"]

        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate(inputs.encode())

        decoded_stdout = stdout.decode()
        assert "Data ingestion complete" in decoded_stdout
        decoded_stderr = stderr.decode()
        assert "Ray" in decoded_stderr

        ##################
        # PRIVATE GPT
        ##################

        inputs = "When was NATO created?\nexit\n"

        app_path = Path("apps", "privategpt", "privateGPT.py")

        command = ["python", app_path]

        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate(inputs.encode())

        decoded_stdout = stdout.decode()
        assert "April 4, 1949" in decoded_stdout
