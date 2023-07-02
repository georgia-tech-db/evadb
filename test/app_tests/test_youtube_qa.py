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
import subprocess
import unittest
from pathlib import Path
from test.markers import chatgpt_skip_marker
from test.util import get_evadb_for_testing, shutdown_ray


class YoutubeQATest(unittest.TestCase):
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

    @chatgpt_skip_marker
    def test_should_run_youtube_qa_app(self):
        app_path = Path("apps", "youtube_qa", "youtube_qa.py")
        input1 = "yes\n\n"  # Go with online video and default URL
        # Assuming that OPENAI_KEY is already set as an environment variable
        input2 = "What is this video on?\n"  # Question
        input3 = "exit\nexit\n"  # Exit
        inputs = input1 + input2 + input3
        command = ["python", app_path]

        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate(inputs.encode())

        decoded_stdout = stdout.decode()
        assert "Julia" or "Rate limit" in decoded_stdout
        print(decoded_stdout)
        print(stderr.decode())
        # decoded_stderr = stderr.decode()
        # assert "Ray" in decoded_stderr
